import os
import hmac
import hashlib
import base64
import logging
from typing import Dict, Any, Optional
import httpx

from app.communication.base import SMSProvider
from app.config import settings

logger = logging.getLogger(__name__)


def normalize_phone_number(phone: Optional[str]) -> str:
    """
    Normalizes phone numbers to standard E.164 format (e.g., +919876543210).
    Handles raw 10-digit Indian numbers, numbers with leading 0, and E.164 formats.
    """
    if not phone:
        return ""
    # Strip whitespace and common punctuation
    cleaned = "".join(ch for ch in phone.strip() if ch.isdigit() or ch == "+")
    
    if cleaned.startswith("+"):
        digits = "".join(filter(str.isdigit, cleaned))
        return f"+{digits}"
    
    digits = "".join(filter(str.isdigit, cleaned))
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 11 and digits.startswith("0"):
        return f"+91{digits[1:]}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    
    return f"+{digits}" if digits else ""


def mask_phone_number(phone: Optional[str]) -> str:
    """
    Masks phone numbers for officer/UI privacy, displaying only the last 4 digits.
    Example: +919876543210 -> ******3210
    """
    if not phone:
        return "Unknown"
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) >= 4:
        return f"******{digits[-4:]}"
    return "******"


def verify_twilio_signature(
    url: str,
    params: Dict[str, Any],
    signature: Optional[str],
    auth_token: Optional[str],
) -> bool:
    """
    Verifies Twilio webhook X-Twilio-Signature using HMAC-SHA1.
    Standard Twilio algorithm:
    1. Start with full webhook URL.
    2. Sort POST parameters alphabetically by key.
    3. Concatenate each key and value to the URL with no separator.
    4. Compute HMAC-SHA1 using auth_token, then base64-encode.
    5. Compare against provided signature using constant-time comparison.
    """
    if not signature or not auth_token:
        return False

    # Build signature base string
    data_to_sign = url
    for key in sorted(params.keys()):
        val = params[key]
        data_to_sign += f"{key}{val}"

    computed_hmac = hmac.new(
        auth_token.encode("utf-8"),
        data_to_sign.encode("utf-8"),
        hashlib.sha1
    ).digest()
    expected_signature = base64.b64encode(computed_hmac).decode("utf-8")

    return hmac.compare_digest(expected_signature, signature)


TRIAL_RESTRICTION_NOTICE = "Twilio Trial restriction: custom Meghvani SMS reply not permitted."


def is_trial_template_error(status_code: int, response_text: str) -> bool:
    """
    Checks if Twilio response indicates trial account template restrictions (e.g. error 57206).
    """
    if status_code == 400:
        if "57206" in response_text:
            return True
        if "predefined SMS templates" in response_text or "predefined templates" in response_text:
            return True
        if "Invalid template name" in response_text:
            return True
    return False


class TwilioSMSProvider(SMSProvider):
    """
    Real SMS Provider using Twilio REST API.
    Does not depend on external SDK - uses standard httpx client with HTTP Basic Auth.
    Includes isolated TRIAL/DEMO mode for Twilio Trial account template restrictions.
    """
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_phone_number: Optional[str] = None,
        trial_mode: Optional[bool] = None,
        trial_template_name: Optional[str] = None,
    ):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID") or settings.twilio_account_sid
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN") or settings.twilio_auth_token
        self.from_phone_number = from_phone_number or os.getenv("TWILIO_PHONE_NUMBER") or settings.twilio_phone_number

        # Trial mode configuration
        if trial_mode is not None:
            self.trial_mode = trial_mode
        else:
            env_trial = os.getenv("TWILIO_TRIAL_MODE")
            if env_trial is not None:
                self.trial_mode = env_trial.strip().lower() in ("true", "1", "yes")
            else:
                self.trial_mode = getattr(settings, "twilio_trial_mode", False)

        self.trial_template_name = (
            trial_template_name
            or os.getenv("TWILIO_TRIAL_TEMPLATE_NAME")
            or getattr(settings, "twilio_trial_template_name", "sms_2fa")
        )

        self._check_credentials()

    def _check_credentials(self) -> None:
        """Validates that necessary Twilio credentials are provided."""
        missing = []
        if not self.account_sid:
            missing.append("TWILIO_ACCOUNT_SID")
        if not self.auth_token:
            missing.append("TWILIO_AUTH_TOKEN")
        if not self.from_phone_number:
            missing.append("TWILIO_PHONE_NUMBER")
        
        if missing:
            err_msg = f"TwilioSMSProvider configuration error: Missing required credentials: {', '.join(missing)}"
            logger.warning(err_msg)
            self.config_error = err_msg
        else:
            self.config_error = None

    def send(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Sends an outbound SMS via Twilio Messages API.
        Handles standard custom messages, and isolated TRIAL/DEMO mode for Twilio trial restrictions.
        Preserves the actual Meghvani reply message in logs and response metadata.
        """
        if self.config_error:
            logger.error(f"Cannot send SMS via Twilio: {self.config_error}")
            return {
                "status": "FAILED",
                "provider_message_id": None,
                "channel": "SMS",
                "provider": "TWILIO",
                "error": self.config_error,
                "actual_message": message,
            }

        normalized_to = normalize_phone_number(phone_number)
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

        def _dispatch_trial_template(client: httpx.Client) -> Dict[str, Any]:
            logger.warning(
                f"Twilio Trial limitation encountered for {mask_phone_number(normalized_to)}: "
                f"{TRIAL_RESTRICTION_NOTICE}"
            )
            trial_payload = {
                "To": normalized_to,
                "From": self.from_phone_number,
                "Body": self.trial_template_name,
            }
            trial_resp = client.post(
                url,
                data=trial_payload,
                auth=(self.account_sid, self.auth_token),
            )
            if trial_resp.status_code in (200, 201):
                res_data = trial_resp.json()
                msg_sid = res_data.get("sid")
                logger.info(
                    f"Twilio Trial pre-approved SMS template '{self.trial_template_name}' sent to "
                    f"{mask_phone_number(normalized_to)}, sid={msg_sid}"
                )
                return {
                    "status": "SENT",
                    "provider_message_id": msg_sid,
                    "channel": "SMS",
                    "provider": "TWILIO",
                    "phone_number": normalized_to,
                    "trial_mode": True,
                    "trial_template": self.trial_template_name,
                    "trial_notice": TRIAL_RESTRICTION_NOTICE,
                    "actual_message": message,
                }
            else:
                err_text = trial_resp.text
                logger.error(f"Twilio Trial API error HTTP {trial_resp.status_code}: {err_text}")
                return {
                    "status": "FAILED",
                    "provider_message_id": None,
                    "channel": "SMS",
                    "provider": "TWILIO",
                    "error": TRIAL_RESTRICTION_NOTICE,
                    "trial_mode": True,
                    "trial_notice": TRIAL_RESTRICTION_NOTICE,
                    "details": f"Twilio HTTP {trial_resp.status_code}: {err_text}",
                    "actual_message": message,
                }

        try:
            with httpx.Client(timeout=10.0) as client:
                # If explicitly configured in trial mode, send predefined trial template
                if self.trial_mode:
                    return _dispatch_trial_template(client)

                # Standard dispatch with custom message body (non-trial accounts)
                data = {
                    "To": normalized_to,
                    "From": self.from_phone_number,
                    "Body": message,
                }
                response = client.post(
                    url,
                    data=data,
                    auth=(self.account_sid, self.auth_token),
                )

                if response.status_code in (200, 201):
                    res_data = response.json()
                    msg_sid = res_data.get("sid")
                    logger.info(f"Twilio SMS sent to {mask_phone_number(normalized_to)}, sid={msg_sid}")
                    return {
                        "status": "SENT",
                        "provider_message_id": msg_sid,
                        "channel": "SMS",
                        "provider": "TWILIO",
                        "phone_number": normalized_to,
                        "actual_message": message,
                    }

                # Check if trial restriction triggered
                if is_trial_template_error(response.status_code, response.text):
                    logger.warning(
                        f"Twilio rejected custom message due to trial restriction (code 57206). "
                        f"Attempting fallback to trial template '{self.trial_template_name}'."
                    )
                    return _dispatch_trial_template(client)

                # Other standard Twilio API errors
                err_text = response.text
                logger.error(f"Twilio API error HTTP {response.status_code}: {err_text}")
                return {
                    "status": "FAILED",
                    "provider_message_id": None,
                    "channel": "SMS",
                    "provider": "TWILIO",
                    "error": f"Twilio HTTP {response.status_code}: {err_text}",
                    "actual_message": message,
                }

        except Exception as e:
            logger.exception(f"Twilio SMS dispatch exception: {e}")
            return {
                "status": "FAILED",
                "provider_message_id": None,
                "channel": "SMS",
                "provider": "TWILIO",
                "error": str(e),
                "actual_message": message,
            }
