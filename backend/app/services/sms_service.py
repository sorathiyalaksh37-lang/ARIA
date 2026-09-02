"""
Twilio SMS Integration Service
Provides SMS notifications with delivery tracking and email fallback
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.core.config import settings
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class SMSService:
    """Twilio SMS service with fallback to email"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_PHONE_NUMBER
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Twilio client"""
        try:
            if self.account_sid and self.auth_token:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized successfully")
            else:
                logger.warning("Twilio credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.client = None
    
    async def send_sms(
        self,
        to: str,
        message: str,
        fallback_email: Optional[str] = None
    ) -> Dict:
        """
        Send SMS with email fallback
        
        Args:
            to: Phone number in E.164 format (+1234567890)
            message: SMS message (max 1600 chars)
            fallback_email: Email to use if SMS fails
            
        Returns:
            Dict with status, message_sid, error
        """
        if not self.client:
            logger.warning("Twilio client not available, using email fallback")
            if fallback_email:
                return await self._fallback_to_email(fallback_email, message)
            return {
                "status": "failed",
                "error": "SMS service not configured",
                "message_sid": None
            }
        
        try:
            # Validate phone number format
            if not to.startswith("+"):
                to = f"+{to}"
            
            # Send SMS
            message_obj = self.client.messages.create(
                body=message[:1600],  # Twilio limit
                from_=self.from_number,
                to=to
            )
            
            logger.info(f"SMS sent successfully: {message_obj.sid}")
            
            return {
                "status": "sent",
                "message_sid": message_obj.sid,
                "to": to,
                "sent_at": datetime.utcnow().isoformat(),
                "error": None
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e.code} - {e.msg}")
            
            # Try email fallback
            if fallback_email:
                return await self._fallback_to_email(fallback_email, message)
            
            return {
                "status": "failed",
                "error": f"Twilio error: {e.msg}",
                "error_code": e.code,
                "message_sid": None
            }
            
        except Exception as e:
            logger.error(f"SMS send error: {str(e)}")
            
            # Try email fallback
            if fallback_email:
                return await self._fallback_to_email(fallback_email, message)
            
            return {
                "status": "failed",
                "error": str(e),
                "message_sid": None
            }
    
    async def _fallback_to_email(self, email: str, message: str) -> Dict:
        """Send notification via email when SMS fails"""
        try:
            result = await email_service.send_email(
                to=email,
                subject="Emergency Notification (SMS Fallback)",
                html_content=f"""
                <div style="font-family: Arial, sans-serif;">
                    <h2>Emergency Notification</h2>
                    <p>This message was sent via email because SMS delivery failed.</p>
                    <div style="background: #f5f5f5; padding: 15px; border-left: 4px solid #dc2626;">
                        {message}
                    </div>
                </div>
                """
            )
            
            if result["status"] == "sent":
                return {
                    "status": "sent_via_email",
                    "message_id": result.get("message_id"),
                    "to": email,
                    "sent_at": datetime.utcnow().isoformat(),
                    "error": None
                }
            else:
                return {
                    "status": "failed",
                    "error": "Both SMS and email fallback failed",
                    "message_sid": None
                }
                
        except Exception as e:
            logger.error(f"Email fallback error: {str(e)}")
            return {
                "status": "failed",
                "error": f"Email fallback failed: {str(e)}",
                "message_sid": None
            }
    
    async def send_bulk_sms(
        self,
        recipients: List[Dict[str, str]],
        message: str
    ) -> Dict:
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of dicts with 'phone' and optional 'email'
            message: SMS message
            
        Returns:
            Dict with success_count, failed_count, results
        """
        results = []
        success_count = 0
        failed_count = 0
        
        for recipient in recipients:
            phone = recipient.get("phone")
            email = recipient.get("email")
            
            if not phone:
                failed_count += 1
                results.append({
                    "recipient": recipient,
                    "status": "failed",
                    "error": "No phone number provided"
                })
                continue
            
            result = await self.send_sms(phone, message, email)
            
            if result["status"] in ["sent", "sent_via_email"]:
                success_count += 1
            else:
                failed_count += 1
            
            results.append({
                "recipient": recipient,
                **result
            })
        
        return {
            "total": len(recipients),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }
    
    async def get_message_status(self, message_sid: str) -> Optional[Dict]:
        """
        Get delivery status of a sent message
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dict with status, error_code, error_message
        """
        if not self.client:
            return None
        
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "date_updated": message.date_updated.isoformat() if message.date_updated else None,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "price": message.price,
                "price_unit": message.price_unit
            }
            
        except TwilioRestException as e:
            logger.error(f"Failed to fetch message status: {e.msg}")
            return None
        except Exception as e:
            logger.error(f"Message status error: {str(e)}")
            return None
    
    async def send_emergency_alert(
        self,
        phone: str,
        incident_id: str,
        severity: str,
        location: str,
        email: Optional[str] = None
    ) -> Dict:
        """Send emergency incident alert"""
        message = f"""
🚨 EMERGENCY ALERT

Incident: #{incident_id}
Severity: {severity.upper()}
Location: {location}

ARIA Emergency Response System
        """.strip()
        
        return await self.send_sms(phone, message, email)
    
    async def send_ambulance_dispatch(
        self,
        phone: str,
        ambulance_id: str,
        incident_location: str,
        hospital_name: str,
        eta_minutes: int,
        email: Optional[str] = None
    ) -> Dict:
        """Send ambulance dispatch notification"""
        message = f"""
🚑 DISPATCH NOTIFICATION

Ambulance: {ambulance_id}
Incident Location: {incident_location}
Destination: {hospital_name}
ETA: {eta_minutes} minutes

ARIA Emergency Response
        """.strip()
        
        return await self.send_sms(phone, message, email)
    
    async def send_hospital_alert(
        self,
        phone: str,
        patient_severity: str,
        estimated_arrival: int,
        special_requirements: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict:
        """Send hospital preparation alert"""
        message = f"""
🏥 INCOMING PATIENT

Severity: {patient_severity}
ETA: {estimated_arrival} minutes
        """.strip()
        
        if special_requirements:
            message += f"\nSpecial Needs: {special_requirements}"
        
        message += "\n\nPrepare for arrival - ARIA"
        
        return await self.send_sms(phone, message, email)


# Global instance
sms_service = SMSService()
