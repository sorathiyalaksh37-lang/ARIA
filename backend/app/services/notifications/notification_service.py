"""
Notification Orchestrator Service
Coordinates SMS and Email notifications with fallbacks and user preferences.
"""
import logging
from typing import List, Dict, Optional, Any
from enum import Enum

from app.services.notifications.sms_service import sms_service
from app.services.notifications.email_service import email_service
from app.services.notifications.templates import templates

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Notification types."""
    INCIDENT_CREATED = "incident_created"
    AMBULANCE_DISPATCHED = "ambulance_dispatched"
    PATIENT_EN_ROUTE = "patient_en_route"
    BLOOD_REQUIRED = "blood_required"
    PLAN_APPROVED = "plan_approved"
    PLAN_REJECTED = "plan_rejected"
    FAMILY_NOTIFICATION = "family_notification"
    INCIDENT_COMPLETED = "incident_completed"
    SYSTEM_ALERT = "system_alert"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    SMS = "sms"
    EMAIL = "email"
    BOTH = "both"


class NotificationService:
    """Orchestrates all notifications with intelligent routing and fallbacks."""
    
    def __init__(self):
        """Initialize notification service."""
        self.sms = sms_service
        self.email = email_service
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipient: Dict[str, Any],
        data: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: Optional[List[NotificationChannel]] = None
    ) -> Dict[str, Any]:
        """
        Send notification through appropriate channels.
        
        Args:
            notification_type: Type of notification
            recipient: {
                "name": str,
                "email": str,
                "phone": str,
                "preferences": {
                    "sms": bool,
                    "email": bool,
                    "preferred_channel": str
                }
            }
            data: Dynamic data for template
            priority: Notification priority
            channels: Override channels (optional)
            
        Returns:
            {
                "sms_result": Dict,
                "email_result": Dict,
                "success": bool,
                "channels_used": List[str]
            }
        """
        # Determine channels to use
        if channels is None:
            channels = self._determine_channels(recipient, priority)
        
        results = {
            "sms_result": None,
            "email_result": None,
            "success": False,
            "channels_used": []
        }
        
        # Send SMS
        if NotificationChannel.SMS in channels and recipient.get("phone"):
            sms_result = await self._send_sms_notification(
                notification_type, recipient, data, priority
            )
            results["sms_result"] = sms_result
            if sms_result and sms_result.get("status") != "failed":
                results["channels_used"].append("sms")
                results["success"] = True
        
        # Send Email
        if NotificationChannel.EMAIL in channels and recipient.get("email"):
            email_result = await self._send_email_notification(
                notification_type, recipient, data
            )
            results["email_result"] = email_result
            if email_result and email_result.get("status_code") in [200, 202]:
                results["channels_used"].append("email")
                results["success"] = True
        
        # Fallback: If SMS failed and it's emergency, try email
        if (priority == NotificationPriority.EMERGENCY and 
            not results["sms_result"] and 
            recipient.get("email")):
            logger.warning(f"SMS failed for emergency, falling back to email")
            email_result = await self._send_email_notification(
                notification_type, recipient, data
            )
            results["email_result"] = email_result
            if email_result:
                results["channels_used"].append("email")
                results["success"] = True
        
        return results
    
    async def send_batch_notification(
        self,
        notification_type: NotificationType,
        recipients: List[Dict[str, Any]],
        data: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> List[Dict[str, Any]]:
        """
        Send notification to multiple recipients.
        
        Args:
            notification_type: Type of notification
            recipients: List of recipient dictionaries
            data: Shared data for template
            priority: Notification priority
            
        Returns:
            List of results
        """
        results = []
        for recipient in recipients:
            result = await self.send_notification(
                notification_type, recipient, data, priority
            )
            results.append({
                "recipient": recipient.get("name", recipient.get("email")),
                **result
            })
        
        success_count = sum(1 for r in results if r["success"])
        logger.info(
            f"Batch notification: {success_count}/{len(recipients)} successful"
        )
        
        return results
    
    def _determine_channels(
        self,
        recipient: Dict[str, Any],
        priority: NotificationPriority
    ) -> List[NotificationChannel]:
        """
        Determine which channels to use based on preferences and priority.
        
        Args:
            recipient: Recipient information
            priority: Notification priority
            
        Returns:
            List of channels to use
        """
        preferences = recipient.get("preferences", {})
        
        # Emergency priority: use all available channels
        if priority == NotificationPriority.EMERGENCY:
            channels = []
            if recipient.get("phone"):
                channels.append(NotificationChannel.SMS)
            if recipient.get("email"):
                channels.append(NotificationChannel.EMAIL)
            return channels
        
        # Respect user preferences
        channels = []
        
        if preferences.get("sms", True) and recipient.get("phone"):
            channels.append(NotificationChannel.SMS)
        
        if preferences.get("email", True) and recipient.get("email"):
            channels.append(NotificationChannel.EMAIL)
        
        # Default to email if no preferences set
        if not channels and recipient.get("email"):
            channels.append(NotificationChannel.EMAIL)
        
        return channels
    
    async def _send_sms_notification(
        self,
        notification_type: NotificationType,
        recipient: Dict[str, Any],
        data: Dict[str, Any],
        priority: NotificationPriority
    ) -> Optional[Dict]:
        """Send SMS notification."""
        # Get template
        message = self._get_sms_template(notification_type, data)
        
        if not message:
            logger.error(f"No SMS template for {notification_type}")
            return None
        
        # Send SMS
        return await self.sms.send_sms(
            to=recipient["phone"],
            message=message,
            priority=priority.value
        )
    
    async def _send_email_notification(
        self,
        notification_type: NotificationType,
        recipient: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Optional[Dict]:
        """Send email notification."""
        # Get template
        html_content = self._get_email_template(notification_type, data)
        
        if not html_content:
            logger.error(f"No email template for {notification_type}")
            return None
        
        # Get subject
        subject = self._get_email_subject(notification_type, data)
        
        # Get plain text version
        plain_content = templates.get_plain_text_version(html_content)
        
        # Send email
        return await self.email.send_email(
            to=recipient["email"],
            subject=subject,
            html_content=html_content,
            plain_content=plain_content
        )
    
    def _get_sms_template(
        self,
        notification_type: NotificationType,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """Get SMS template for notification type."""
        template_map = {
            NotificationType.INCIDENT_CREATED: templates.sms_incident_created,
            NotificationType.AMBULANCE_DISPATCHED: templates.sms_ambulance_dispatched,
            NotificationType.PATIENT_EN_ROUTE: templates.sms_patient_en_route,
            NotificationType.BLOOD_REQUIRED: templates.sms_blood_required,
            NotificationType.PLAN_APPROVED: templates.sms_plan_approved,
            NotificationType.PLAN_REJECTED: templates.sms_plan_rejected,
            NotificationType.FAMILY_NOTIFICATION: templates.sms_family_notification,
        }
        
        template_func = template_map.get(notification_type)
        if template_func:
            return template_func(data)
        return None
    
    def _get_email_template(
        self,
        notification_type: NotificationType,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """Get email template for notification type."""
        template_map = {
            NotificationType.INCIDENT_CREATED: templates.email_incident_created,
            NotificationType.AMBULANCE_DISPATCHED: templates.email_ambulance_dispatched,
            NotificationType.PATIENT_EN_ROUTE: templates.email_patient_en_route,
        }
        
        template_func = template_map.get(notification_type)
        if template_func:
            return template_func(data)
        return None
    
    def _get_email_subject(
        self,
        notification_type: NotificationType,
        data: Dict[str, Any]
    ) -> str:
        """Get email subject for notification type."""
        subject_map = {
            NotificationType.INCIDENT_CREATED: f"🚨 New Emergency Incident: {data.get('incident_id')}",
            NotificationType.AMBULANCE_DISPATCHED: f"🚑 Ambulance Dispatched: {data.get('ambulance_id')}",
            NotificationType.PATIENT_EN_ROUTE: f"🏥 Patient En Route - ETA {data.get('eta')} min",
            NotificationType.BLOOD_REQUIRED: f"🩸 Urgent: Blood Required - {data.get('blood_type')}",
            NotificationType.PLAN_APPROVED: f"✅ Response Plan Approved: {data.get('incident_id')}",
            NotificationType.PLAN_REJECTED: f"❌ Plan Rejected: {data.get('incident_id')}",
            NotificationType.FAMILY_NOTIFICATION: f"Emergency Update: {data.get('patient_name')}",
            NotificationType.INCIDENT_COMPLETED: f"✅ Incident Completed: {data.get('incident_id')}",
            NotificationType.SYSTEM_ALERT: "ARIA System Alert",
        }
        
        return subject_map.get(
            notification_type,
            f"ARIA Notification: {notification_type.value}"
        )


# Global instance
notification_service = NotificationService()
