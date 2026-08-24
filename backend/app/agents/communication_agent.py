"""
ARIA Communication Agent
Sends notifications to stakeholders (hospital, ambulance, reporter)
"""
from typing import List, Dict, Any
from datetime import datetime
import httpx
from twilio.rest import Client as TwilioClient

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, WorkflowStatus
from app.core.config import settings


class CommunicationAgent(BaseAgent):
    """
    Communication Agent: Notifies all stakeholders about the emergency response plan.
    Sends notifications via SMS, email, and WebSocket.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        enable_sms: bool = True,
        enable_email: bool = True,
        enable_websocket: bool = True
    ):
        """
        Initialize communication agent.
        
        Args:
            max_retries: Maximum retries
            enable_sms: Enable SMS notifications
            enable_email: Enable email notifications
            enable_websocket: Enable WebSocket notifications
        """
        super().__init__(name="CommunicationAgent", max_retries=max_retries)
        self.enable_sms = enable_sms
        self.enable_email = enable_email
        self.enable_websocket = enable_websocket
        
        # Initialize Twilio client if SMS enabled
        self.twilio_client = None
        if self.enable_sms and hasattr(settings, "TWILIO_ACCOUNT_SID"):
            try:
                self.twilio_client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.logger.info("✅ Twilio SMS client initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Twilio: {e}")
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Send notifications to all stakeholders.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with notification records
        """
        self._log_state_update(
            "Starting stakeholder notifications",
            incident_id=state.incident.incident_id
        )
        
        # Validate response plan exists
        if not state.response_plan:
            raise ValueError("Response plan required before sending notifications")
        
        notifications_sent = []
        
        # 1. Notify Hospital
        if state.response_plan.selected_hospital:
            try:
                await self._notify_hospital(state)
                notifications_sent.append("Hospital notified successfully")
                self.logger.info("✅ Hospital notified")
            except Exception as e:
                self.logger.error(f"❌ Failed to notify hospital: {e}")
                notifications_sent.append(f"Hospital notification failed: {str(e)}")
        
        # 2. Notify Ambulance
        if state.response_plan.selected_ambulance:
            try:
                await self._notify_ambulance(state)
                notifications_sent.append("Ambulance dispatched successfully")
                self.logger.info("✅ Ambulance dispatched")
            except Exception as e:
                self.logger.error(f"❌ Failed to dispatch ambulance: {e}")
                notifications_sent.append(f"Ambulance dispatch failed: {str(e)}")
        
        # 3. Notify Blood Bank (if needed)
        if state.response_plan.selected_blood_bank:
            try:
                await self._notify_blood_bank(state)
                notifications_sent.append("Blood bank notified successfully")
                self.logger.info("✅ Blood bank notified")
            except Exception as e:
                self.logger.error(f"❌ Failed to notify blood bank: {e}")
                notifications_sent.append(f"Blood bank notification failed: {str(e)}")
        
        # 4. Notify Reporter
        if state.incident.reporter_phone:
            try:
                await self._notify_reporter(state)
                notifications_sent.append("Reporter notified successfully")
                self.logger.info("✅ Reporter notified")
            except Exception as e:
                self.logger.error(f"❌ Failed to notify reporter: {e}")
                notifications_sent.append(f"Reporter notification failed: {str(e)}")
        
        # 5. Broadcast via WebSocket
        if self.enable_websocket:
            try:
                await self._broadcast_websocket(state)
                notifications_sent.append("WebSocket broadcast sent")
                self.logger.info("✅ WebSocket broadcast sent")
            except Exception as e:
                self.logger.error(f"❌ Failed WebSocket broadcast: {e}")
                notifications_sent.append(f"WebSocket broadcast failed: {str(e)}")
        
        # Update response plan with notification records
        state.response_plan.notifications_sent = notifications_sent
        
        self._log_state_update(
            "Notifications completed",
            notifications_sent=len(notifications_sent),
            success_count=sum(1 for n in notifications_sent if "successfully" in n)
        )
        
        return state
    
    async def _notify_hospital(self, state: AgentState):
        """
        Send notification to hospital.
        
        Args:
            state: Agent state
        """
        hospital = state.response_plan.selected_hospital
        ambulance = state.response_plan.selected_ambulance
        
        message = (
            f"🚨 EMERGENCY ALERT\n"
            f"Incident ID: {state.incident.incident_id}\n"
            f"Severity: {state.response_plan.severity.value}\n"
            f"Patient ETA: {ambulance.eta_minutes:.0f} min\n"
            f"Ambulance: {ambulance.registration_number} ({ambulance.ambulance_type})\n"
            f"Description: {state.incident.description[:100]}\n"
            f"Please prepare: {', '.join(state.triage_result.recommended_resources[:3])}"
        )
        
        # Send via SMS
        if self.enable_sms and hospital.contact_phone:
            await self._send_sms(hospital.contact_phone, message)
        
        # Send via email (if implemented)
        if self.enable_email and hasattr(hospital, "email"):
            await self._send_email(
                to=hospital.email,
                subject=f"Emergency Alert: {state.incident.incident_id}",
                body=message
            )
    
    async def _notify_ambulance(self, state: AgentState):
        """
        Send dispatch notification to ambulance.
        
        Args:
            state: Agent state
        """
        ambulance = state.response_plan.selected_ambulance
        hospital = state.response_plan.selected_hospital
        
        message = (
            f"🚑 DISPATCH\n"
            f"Incident: {state.incident.incident_id}\n"
            f"Severity: {state.response_plan.severity.value}\n"
            f"Location: {state.incident.location.latitude:.4f}, {state.incident.location.longitude:.4f}\n"
            f"Destination: {hospital.name}\n"
            f"Hospital: {hospital.location.latitude:.4f}, {hospital.location.longitude:.4f}\n"
            f"Description: {state.incident.description[:100]}\n"
            f"ETA: {ambulance.eta_minutes:.0f} min"
        )
        
        # Send via SMS
        if self.enable_sms and ambulance.driver_phone:
            await self._send_sms(ambulance.driver_phone, message)
    
    async def _notify_blood_bank(self, state: AgentState):
        """
        Send notification to blood bank.
        
        Args:
            state: Agent state
        """
        blood_bank = state.response_plan.selected_blood_bank
        required_type = state.context.get("required_blood_type", "Type needed")
        
        message = (
            f"🩸 BLOOD REQUEST\n"
            f"Incident: {state.incident.incident_id}\n"
            f"Blood Type: {required_type}\n"
            f"Severity: {state.response_plan.severity.value}\n"
            f"Destination: {state.response_plan.selected_hospital.name}\n"
            f"Please prepare blood units for emergency transport"
        )
        
        # Send via SMS
        if self.enable_sms and blood_bank.contact_phone:
            await self._send_sms(blood_bank.contact_phone, message)
    
    async def _notify_reporter(self, state: AgentState):
        """
        Send acknowledgment to incident reporter.
        
        Args:
            state: Agent state
        """
        ambulance = state.response_plan.selected_ambulance
        
        message = (
            f"ARIA Emergency Response\n"
            f"Incident: {state.incident.incident_id}\n"
            f"Help is on the way!\n"
            f"Ambulance: {ambulance.registration_number}\n"
            f"ETA: {ambulance.eta_minutes:.0f} minutes\n"
            f"Stay calm and keep the patient stable.\n"
            f"Emergency services have been notified."
        )
        
        # Send via SMS
        if self.enable_sms and state.incident.reporter_phone:
            await self._send_sms(state.incident.reporter_phone, message)
    
    async def _send_sms(self, phone_number: str, message: str):
        """
        Send SMS via Twilio.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message
        """
        if not self.twilio_client:
            self.logger.warning("Twilio not configured - SMS not sent")
            return
        
        try:
            # Send SMS
            sms = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            self.logger.info(f"📱 SMS sent to {phone_number}: {sms.sid}")
        except Exception as e:
            self.logger.error(f"Failed to send SMS to {phone_number}: {e}")
            raise
    
    async def _send_email(self, to: str, subject: str, body: str):
        """
        Send email notification.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
        """
        # Placeholder for email sending
        # In production, integrate with SendGrid, AWS SES, etc.
        self.logger.info(f"📧 Email would be sent to {to}: {subject}")
    
    async def _broadcast_websocket(self, state: AgentState):
        """
        Broadcast update via WebSocket.
        
        Args:
            state: Agent state
        """
        try:
            # Prepare WebSocket message
            ws_message = {
                "event": "incident.plan_generated",
                "incident_id": state.incident.incident_id,
                "plan_id": state.response_plan.plan_id,
                "severity": state.response_plan.severity.value,
                "hospital": {
                    "id": state.response_plan.selected_hospital.hospital_id,
                    "name": state.response_plan.selected_hospital.name
                } if state.response_plan.selected_hospital else None,
                "ambulance": {
                    "id": state.response_plan.selected_ambulance.ambulance_id,
                    "registration": state.response_plan.selected_ambulance.registration_number,
                    "eta": state.response_plan.selected_ambulance.eta_minutes
                } if state.response_plan.selected_ambulance else None,
                "estimated_time": state.response_plan.estimated_total_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to WebSocket service
            # In production, this would connect to WebSocket manager
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.WEBSOCKET_SERVICE_URL}/broadcast",
                    json=ws_message,
                    timeout=5.0
                )
            
        except Exception as e:
            self.logger.warning(f"WebSocket broadcast failed: {e}")
            # Don't raise - WebSocket failure shouldn't stop workflow
