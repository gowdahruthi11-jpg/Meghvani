from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.registration_session import RegistrationSession
from app.models.village import Village
from app.models.block import Block
from app.models.crop import Crop
from app.schemas.farmer import FarmerCreate
from app.services.farmer_service import FarmerService
from app.services.location_service import LocationService

LANGUAGES = {
    "1": "Hindi",
    "2": "Marathi",
    "3": "Kannada",
    "4": "English"
}

LANGUAGE_PROMPT = (
    "Welcome to Meghvani.\n"
    "Select language:\n"
    "1 Hindi\n"
    "2 Marathi\n"
    "3 Kannada\n"
    "4 English\n"
    "Reply with number (1-4)."
)

class RegistrationService:
    @staticmethod
    def get_or_create_session(db: Session, phone_number: str) -> RegistrationSession:
        clean_phone = phone_number.strip()
        session = db.query(RegistrationSession).filter(
            RegistrationSession.phone_number == clean_phone
        ).first()

        now = datetime.now(timezone.utc)
        if not session:
            session = RegistrationSession(
                phone_number=clean_phone,
                current_step="START",
                created_at=now,
                updated_at=now,
                expires_at=now + timedelta(minutes=60)
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        else:
            # Check if expired
            if session.expires_at and session.expires_at.tzinfo is None:
                session_expires = session.expires_at.replace(tzinfo=timezone.utc)
            else:
                session_expires = session.expires_at

            if session_expires and now > session_expires:
                session.current_step = "START"
                session.language = None
                session.pin_code = None
                session.selected_village_id = None
                session.selected_block_id = None
                session.selected_crop_id = None
                session.consent = False
                session.expires_at = now + timedelta(minutes=60)
                db.commit()
                db.refresh(session)

        return session

    @classmethod
    def find_farmer_by_phone(cls, db: Session, phone_number: str) -> Optional[Farmer]:
        """
        Finds a farmer matching exact phone, normalized E.164, or last 10 digits.
        """
        if not phone_number:
            return None
        clean = phone_number.strip()
        farmer = db.query(Farmer).filter(Farmer.phone_number == clean).first()
        if farmer:
            return farmer

        from app.communication.twilio_sms import normalize_phone_number
        norm = normalize_phone_number(clean)
        if norm:
            farmer = db.query(Farmer).filter(Farmer.phone_number == norm).first()
            if farmer:
                return farmer

        digits = "".join(filter(str.isdigit, clean))
        if len(digits) >= 10:
            last10 = digits[-10:]
            farmer = db.query(Farmer).filter(Farmer.phone_number.endswith(last10)).first()
            if farmer:
                return farmer

        return None

    @classmethod
    def generate_status_advisory(cls, db: Session, farmer: Farmer) -> str:
        """
        Executes the Meghvani multi-event ML prediction and Explainable AI pipeline
        to generate a dynamic, concise SMS advisory for the registered farmer's block.
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            from app.ml.model_loader import explain_block_false_onset
            block_id_norm = f"BLK{farmer.block_id:03d}" if farmer.block_id else "BLK003"
            try:
                xai = explain_block_false_onset(block_id_norm)
            except Exception:
                # Default to canonical profile BLK003 (Amravati Central) if block not found
                xai = explain_block_false_onset("BLK003")

            region_name = xai.get("region_name", farmer.village.name if farmer.village else "Vidarbha")
            prob_pct = xai.get("probability_pct", 28)
            risk_tier = xai.get("risk_tier", "Moderate Risk")
            top_drivers = xai.get("top_drivers", [])
            decision = xai.get("decision", "WAIT")

            driver_lines = []
            for d in top_drivers[:3]:
                label = d.get("label", "Rainfall metric")
                direction = d.get("direction", "NEUTRAL")
                if direction == "REDUCING":
                    driver_lines.append(f"• {label} improving (risk reducing)")
                elif direction == "INCREASING":
                    driver_lines.append(f"• {label} dry streak (risk increasing)")
                else:
                    driver_lines.append(f"• {label} monitored")

            drivers_text = "\n".join(driver_lines) if driver_lines else "• Seasonal progression favorable"

            if decision == "SOW_NOW":
                advice = "Moisture surge adequate. Favorable for sowing."
            elif decision == "SOW_PART_NOW":
                advice = "Moderate risk. Delay full sowing or use seed treatment."
            else:
                advice = "Delay sowing until rainfall is sustained."

            return (
                f"Meghvani Status: Active\n\n"
                f"MEGHVANI ADVISORY\n\n"
                f"{region_name}\n\n"
                f"False onset probability: {prob_pct}%\n"
                f"Risk: {risk_tier.upper()}\n\n"
                f"Why:\n{drivers_text}\n\n"
                f"Advice:\n{advice}\n\n"
                f"Reply STATUS for latest update."
            )
        except Exception as e:
            logger.error(f"Error generating dynamic ML advisory for farmer {farmer.id}: {e}", exc_info=True)
            return "Meghvani received your message, but the advisory service is temporarily unavailable. Please try again shortly."

    @classmethod
    def reset_registration(cls, db: Session, phone_number: str) -> Tuple[str, str, bool, Optional[int]]:
        """
        Deactivates active farmer profile and clears registration session back to START.
        """
        clean_phone = phone_number.strip()
        existing_farmer = cls.find_farmer_by_phone(db, clean_phone)
        if existing_farmer:
            existing_farmer.active = False
            db.commit()

        session = cls.get_or_create_session(db, clean_phone)
        session.current_step = "START"
        session.language = None
        session.pin_code = None
        session.selected_village_id = None
        session.selected_block_id = None
        session.selected_crop_id = None
        session.consent = False
        session.updated_at = datetime.now(timezone.utc)
        session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=60)
        db.commit()
        return "Registration reset. Text MEGH to start fresh.", "START", False, None

    @classmethod
    def start_registration(cls, db: Session, phone_number: str, force_new: bool = False) -> Tuple[str, str, bool, Optional[int]]:
        """
        Starts conversational registration when farmer sends MEGH or calls missed-call number.
        If force_new is True, any existing farmer profile is deactivated to start a fresh demo.
        """
        clean_phone = phone_number.strip()

        # Check if already registered
        existing_farmer = cls.find_farmer_by_phone(db, clean_phone)
        if existing_farmer and existing_farmer.active:
            if force_new:
                existing_farmer.active = False
                db.commit()
            else:
                crop_name = existing_farmer.crop.name if existing_farmer.crop else "Unknown"
                village_name = existing_farmer.village.name if existing_farmer.village else "Unknown"
                msg = (
                    f"You are already registered with Meghvani!\n"
                    f"Village: {village_name} | Crop: {crop_name} | Language: {existing_farmer.preferred_language}\n"
                    f"Reply STATUS for advisory status, or UPDATE to change your preferences."
                )
                return msg, "ALREADY_REGISTERED", True, existing_farmer.id

        session = cls.get_or_create_session(db, clean_phone)
        session.current_step = "LANGUAGE"
        session.language = None
        session.pin_code = None
        session.selected_village_id = None
        session.selected_block_id = None
        session.selected_crop_id = None
        session.consent = False
        session.updated_at = datetime.now(timezone.utc)
        session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=60)
        db.commit()

        return LANGUAGE_PROMPT, "LANGUAGE", False, None

    @classmethod
    def process_message(
        cls, db: Session, phone_number: str, incoming_text: str
    ) -> Tuple[str, str, bool, Optional[int]]:
        """
        Handles state transitions for conversational SMS registration.
        Returns: (reply_message, current_step, is_completed, registered_farmer_id)
        """
        clean_phone = phone_number.strip()
        text = incoming_text.strip()
        upper_text = text.upper()

        # Check for global reset keywords
        if upper_text in ["MEGH", "START", "RESTART"]:
            return cls.start_registration(db, clean_phone)

        # Check if already registered
        existing_farmer = cls.find_farmer_by_phone(db, clean_phone)
        if existing_farmer and existing_farmer.active:
            if upper_text == "STATUS":
                advisory_msg = cls.generate_status_advisory(db, existing_farmer)
                return (
                    advisory_msg,
                    "STATUS",
                    True,
                    existing_farmer.id
                )
            elif upper_text in ["UPDATE", "RESET", "REREGISTER", "REGISTER AGAIN", "REGISTER_AGAIN", "NEW"]:
                # Allow re-registration: deactivate old profile and start fresh at Language selection
                existing_farmer.active = False
                db.commit()
                return cls.start_registration(db, clean_phone, force_new=True)
            else:
                return (
                    "You are already registered with Meghvani. Reply STATUS for advisory info, or UPDATE to update preferences.",
                    "ALREADY_REGISTERED",
                    True,
                    existing_farmer.id
                )

        session = cls.get_or_create_session(db, clean_phone)
        step = session.current_step

        if step == "START":
            return cls.start_registration(db, clean_phone)

        # -------------------------------------------------------------
        # STEP 1: LANGUAGE SELECTION
        # -------------------------------------------------------------
        if step == "LANGUAGE":
            selected_lang = LANGUAGES.get(text)
            if not selected_lang:
                # Also accept raw text names
                for k, v in LANGUAGES.items():
                    if v.lower() == text.lower():
                        selected_lang = v
                        break

            if not selected_lang:
                return (
                    "Invalid choice. Please reply with a valid number:\n1 Hindi\n2 Marathi\n3 Kannada\n4 English",
                    "LANGUAGE",
                    False,
                    None
                )

            session.language = selected_lang
            session.current_step = "PIN"
            session.updated_at = datetime.now(timezone.utc)
            db.commit()
            return "Enter your 6-digit PIN code (e.g. 441501, 442104, 444904).", "PIN", False, None

        # -------------------------------------------------------------
        # STEP 2: PIN CODE ENTRY
        # -------------------------------------------------------------
        if step == "PIN":
            clean_pin = text.replace(" ", "").replace("-", "").strip()
            if not clean_pin.isdigit() or len(clean_pin) != 6:
                return (
                    "Invalid PIN code. Please enter exactly 6 numeric digits (e.g., 440001).",
                    "PIN",
                    False,
                    None
                )

            villages = LocationService.get_villages_by_pin(db, clean_pin)
            if not villages:
                return (
                    f"No villages found for PIN {clean_pin}. Please re-enter a valid 6-digit PIN code.",
                    "PIN",
                    False,
                    None
                )

            session.pin_code = clean_pin
            session.current_step = "VILLAGE"
            session.updated_at = datetime.now(timezone.utc)
            db.commit()

            # Build village selection prompt
            village_lines = [f"{i+1}: {v.name} (District: {v.district})" for i, v in enumerate(villages)]
            prompt = f"PIN {clean_pin} accepted.\nSelect your village:\n" + "\n".join(village_lines) + "\nReply with number (e.g. 1)."
            return prompt, "VILLAGE", False, None

        # -------------------------------------------------------------
        # STEP 3: VILLAGE SELECTION
        # -------------------------------------------------------------
        if step == "VILLAGE":
            if not session.pin_code:
                session.current_step = "PIN"
                db.commit()
                return "Please enter your 6-digit PIN code.", "PIN", False, None

            villages = LocationService.get_villages_by_pin(db, session.pin_code)
            if not text.isdigit():
                return (
                    f"Please reply with a valid number from 1 to {len(villages)} to select your village.",
                    "VILLAGE",
                    False,
                    None
                )

            idx = int(text) - 1
            if idx < 0 or idx >= len(villages):
                return (
                    f"Invalid village option. Please reply with a number between 1 and {len(villages)}.",
                    "VILLAGE",
                    False,
                    None
                )

            chosen_village = villages[idx]
            session.selected_village_id = chosen_village.id
            session.selected_block_id = chosen_village.block_id
            session.current_step = "CROP"
            session.updated_at = datetime.now(timezone.utc)
            db.commit()

            # Retrieve active crops for selection
            crops = db.query(Crop).filter(Crop.active == True).all()
            crop_lines = [f"{i+1}: {c.name}" for i, c in enumerate(crops)]
            prompt = "Select your main crop:\n" + "\n".join(crop_lines) + "\nReply with number (e.g. 1)."
            return prompt, "CROP", False, None

        # -------------------------------------------------------------
        # STEP 4: CROP SELECTION
        # -------------------------------------------------------------
        if step == "CROP":
            crops = db.query(Crop).filter(Crop.active == True).all()
            if not text.isdigit():
                return (
                    f"Please reply with a number between 1 and {len(crops)} to select your crop.",
                    "CROP",
                    False,
                    None
                )

            idx = int(text) - 1
            if idx < 0 or idx >= len(crops):
                return (
                    f"Invalid crop option. Please reply with a number between 1 and {len(crops)}.",
                    "CROP",
                    False,
                    None
                )

            chosen_crop = crops[idx]
            session.selected_crop_id = chosen_crop.id
            session.current_step = "CONSENT"
            session.updated_at = datetime.now(timezone.utc)
            db.commit()

            consent_msg = (
                "You will receive weather and agricultural advisories from Meghvani by SMS/voice/WhatsApp. "
                "Reply YES to continue."
            )
            return consent_msg, "CONSENT", False, None

        # -------------------------------------------------------------
        # STEP 5: CONSENT & FARMER CREATION
        # -------------------------------------------------------------
        if step == "CONSENT":
            if upper_text in ["YES", "Y", "HA", "HO", "HAAN", "OK"]:
                # Create final Farmer profile
                farmer_in = FarmerCreate(
                    phone_number=session.phone_number,
                    preferred_language=session.language or "Hindi",
                    pin_code=session.pin_code or "000000",
                    village_id=session.selected_village_id or 1,
                    block_id=session.selected_block_id or 1,
                    crop_id=session.selected_crop_id or 1,
                    communication_preference="SMS",
                    consent=True
                )
                farmer = FarmerService.create_farmer(db, farmer_in)

                session.current_step = "COMPLETED"
                session.consent = True
                session.updated_at = datetime.now(timezone.utc)
                db.commit()

                success_msg = (
                    "Registration successful. Meghvani will send important weather and crop advisories "
                    f"in your selected language ({farmer.preferred_language})."
                )
                return success_msg, "COMPLETED", True, farmer.id

            elif upper_text in ["NO", "CANCEL", "EXIT"]:
                session.current_step = "START"
                db.commit()
                return "Registration cancelled. Reply MEGH anytime to register.", "START", False, None

            else:
                return (
                    "Only YES activates registration. "
                    "You will receive weather and agricultural advisories from Meghvani. Reply YES to continue.",
                    "CONSENT",
                    False,
                    None
                )

        # Fallback
        return "Unknown state. Reply MEGH to restart registration.", "START", False, None
