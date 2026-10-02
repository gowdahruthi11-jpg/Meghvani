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
    def start_registration(cls, db: Session, phone_number: str) -> Tuple[str, str, bool, Optional[int]]:
        """
        Starts conversational registration when farmer sends MEGH or calls missed-call number.
        """
        clean_phone = phone_number.strip()

        # Check if already registered
        existing_farmer = db.query(Farmer).filter(Farmer.phone_number == clean_phone).first()
        if existing_farmer and existing_farmer.active:
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
        existing_farmer = db.query(Farmer).filter(Farmer.phone_number == clean_phone).first()
        if existing_farmer and existing_farmer.active:
            if upper_text == "STATUS":
                return (
                    f"Meghvani Status: Active\n"
                    f"Registered Crop: {existing_farmer.crop.name}\n"
                    f"Language: {existing_farmer.preferred_language}\n"
                    f"Alert Channel: {existing_farmer.communication_preference}",
                    "STATUS",
                    True,
                    existing_farmer.id
                )
            elif upper_text == "UPDATE":
                # Allow re-registration
                existing_farmer.active = False
                db.commit()
                return cls.start_registration(db, clean_phone)
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
            return "Enter your 6-digit PIN code.", "PIN", False, None

        # -------------------------------------------------------------
        # STEP 2: PIN CODE ENTRY
        # -------------------------------------------------------------
        if step == "PIN":
            if not text.isdigit() or len(text) != 6:
                return (
                    "Invalid PIN code. Please enter exactly 6 numeric digits (e.g., 440001).",
                    "PIN",
                    False,
                    None
                )

            villages = LocationService.get_villages_by_pin(db, text)
            if not villages:
                return (
                    f"No villages found for PIN {text}. Please re-enter a valid 6-digit PIN code.",
                    "PIN",
                    False,
                    None
                )

            session.pin_code = text
            session.current_step = "VILLAGE"
            session.updated_at = datetime.now(timezone.utc)
            db.commit()

            # Build village selection prompt
            village_lines = [f"{i+1}: {v.name} (District: {v.district})" for i, v in enumerate(villages)]
            prompt = "Select your village:\n" + "\n".join(village_lines) + "\nReply with number (e.g. 1)."
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
