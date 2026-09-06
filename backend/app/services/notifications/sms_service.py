"""
SMS Notification Service using Twilio
Sends SMS notifications to users and tracks delivery status.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Twilio SMS service for emergency notifications."""
    
    def __init__(self):
        """Initialize Twilio client."""
        self.client = None
        if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.from_number = settings.TWILIO_PHONE_NUMBER
                logger.info("✅ Twilio SMS client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twilio: {e}")
        else:
            logger.warning("⚠️ Twilio credentials not configured")
    
    def is_available(self) -> bool:
        """Check if SMS service is available."""
        return self.client is not None
    
    async def send_sms(
        self,
        to: str,
        message: str,
        priority: str = "normal"
    ) -> Optional[Dict]:
        """
        Send SMS to a single recipient.
        
        Args:
            to: Recipient phone number (E.164 format: +1234567890)
            message: SMS message text (max 1600 chars)
            priority: Priority level (normal, high, emergency)
            
        Returns:
            {
                "sid": str,
                "status": str,
                "to": str,
                "from": str,
                "timestamp": str,
                "error": str (if failed)
            }
        """
        if not self.is_available():
            logger.error("SMS service not available")
            return None
        
        try:
            # Ensure phone number is in E.164 format
            if not to.startswith("+"):
                logger.warning(f"Phone number not in E.164 format: {to}")
                # Try to add country code (default India +91)
                to = f"+91{to.lstrip('0')}"
            
            # Truncate message if too long
            if len(message) > 1600:
                message = message[:1597] + "..."
                logger.warning(f"Message truncated to 1600 characters")
            
            # Add priority indicator for emergency messages
            if priority == "emergency":
                message = f"🚨 EMERGENCY: {message}"
            elif priority == "high":
                message = f"⚠️ URGENT: {message}"
            
            # Send SMS
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to
            )
            
            result = {
                "sid": msg.sid,
                "status": msg.status,
                "to": msg.to,
                "from": msg.from_,
                "timestamp": datetime.utcnow().isoformat(),
                "provider": "twilio"
            }
            
            logger.info(f"✅ SMS sent to {to}: {msg.sid}")
            return result
            
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e}")
            return {
                "status": "failed",
                "to": to,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return None
    
    async def send_batch_sms(
        self,
        recipients: List[str],
        message: str,
        priority: str = "normal"
    ) -> List[Dict]:
        """
        Send SMS to multiple recipients.
        
        Args:
            recipients: List of phone numbers
            message: SMS message text
            priority: Priority level
            
        Returns:
            List of send results
        """
        results = []
        for phone in recipients:
            result = await self.send_sms(phone, message, priority)
            if result:
                results.append(result)
        
        logger.info(f"Batch SMS: {len(results)}/{len(recipients)} sent successfully")
        return results
    
    async def get_delivery_status(self, message_sid: str) -> Optional[Dict]:
        """
        Get delivery status of a sent message.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Message status information
        """
        if not self.is_available():
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except TwilioRestException as e:
            logger.error(f"Failed to get message status: {e}")
            return None
    
    async def get_batch_status(self, message_sids: List[str]) -> List[Optional[Dict]]:
        """
        Get delivery status for multiple messages.
        
        Args:
            message_sids: List of Twilio message SIDs
            
        Returns:
            List of status information
        """
        results = []
        for sid in message_sids:
            status = await self.get_delivery_status(sid)
            results.append(status)
        return results
    
    def format_phone_number(self, phone: str, country_code: str = "+91") -> str:
        """
        Format phone number to E.164 format.
        
        Args:
            phone: Phone number
            country_code: Country code (default: India +91)
            
        Returns:
            Formatted phone number
        """
        # Remove all non-numeric characters
        phone = "".join(c for c in phone if c.isdigit())
        
        # Add country code if not present
        if not phone.startswith("+"):
            phone = f"{country_code}{phone.lstrip('0')}"
        
        return phone
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid
        """
        if not self.is_available():
            return False
        
        try:
            lookup = self.client.lookups.v1.phone_numbers(phone).fetch()
            return lookup.phone_number is not None
        except:
            return False


# Global instance
sms_service = SMSService()
