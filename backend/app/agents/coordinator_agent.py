"""
ARIA Coordinator Agent
Manages human-in-the-loop approval for critical incidents
"""
import asyncio
from datetime import datetime
from typing import Optional

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, WorkflowStatus, IncidentSeverity
from app.core.config import settings


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent: Manages human approval for critical incidents.
    Implements human-in-the-loop for high-stakes decisions.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        approval_timeout_seconds: int = 300  # 5 minutes
    ):
        """
        Initialize coordinator agent.
        
        Args:
            max_retries: Maximum retries
            approval_timeout_seconds: Time to wait for human approval
        """
        super().__init__(name="CoordinatorAgent", max_retries=max_retries)
        self.approval_timeout = approval_timeout_seconds
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Manage human approval process if required.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with approval status
        """
        self._log_state_update(
            "Starting coordination check",
            incident_id=state.incident.incident_id,
            requires_approval=state.requires_approval
        )
        
        # Check if approval is required
        if not state.requires_approval:
            self.logger.info("ℹ️ No approval required - proceeding automatically")
            state.workflow_status = WorkflowStatus.APPROVED
            return state
        
        # Validate response plan exists
        if not state.response_plan:
            raise ValueError("Response plan required for approval")
        
        self.logger.warning(
            f"⚠️ CRITICAL incident - Human approval required for {state.incident.incident_id}"
        )
        
        # Present plan for approval
        self._present_plan_for_approval(state)
        
        # Wait for approval (with timeout)
        approval_result = await self._wait_for_approval(state)
        
        if approval_result["approved"]:
            # Plan approved
            state.workflow_status = WorkflowStatus.APPROVED
            state.response_plan.approved_by = approval_result.get("approved_by", "System")
            state.response_plan.approved_at = datetime.utcnow()
            state.approval_notes = approval_result.get("notes")
            
            self.logger.info(
                f"✅ Plan approved by {state.response_plan.approved_by}"
            )
            
        else:
            # Plan rejected or timeout
            state.workflow_status = WorkflowStatus.REJECTED
            state.rejection_reason = approval_result.get("reason", "No approval received")
            
            self.logger.warning(
                f"❌ Plan rejected: {state.rejection_reason}"
            )
        
        self._log_state_update(
            "Coordination completed",
            status=state.workflow_status.value,
            approved_by=state.response_plan.approved_by if state.workflow_status == WorkflowStatus.APPROVED else None
        )
        
        return state
    
    def _present_plan_for_approval(self, state: AgentState):
        """
        Present plan details for human review.
        
        Args:
            state: Agent state
        """
        plan = state.response_plan
        
        self.logger.info("=" * 70)
        self.logger.info("🚨 CRITICAL INCIDENT - APPROVAL REQUIRED")
        self.logger.info("=" * 70)
        self.logger.info(f"Incident ID: {state.incident.incident_id}")
        self.logger.info(f"Severity: {plan.severity.value}")
        self.logger.info(f"Description: {state.incident.description}")
        self.logger.info("-" * 70)
        self.logger.info("PROPOSED RESPONSE PLAN:")
        self.logger.info("-" * 70)
        
        if plan.selected_ambulance:
            self.logger.info(
                f"Ambulance: {plan.selected_ambulance.registration_number} "
                f"({plan.selected_ambulance.ambulance_type})"
            )
            self.logger.info(f"  ETA to scene: {plan.selected_ambulance.eta_minutes:.1f} min")
        
        if plan.selected_hospital:
            self.logger.info(f"Hospital: {plan.selected_hospital.name}")
            self.logger.info(
                f"  Distance: {plan.selected_hospital.distance_km:.1f} km, "
                f"ICU beds: {plan.selected_hospital.available_icu_beds}"
            )
        
        if plan.selected_blood_bank:
            self.logger.info(f"Blood Bank: {plan.selected_blood_bank.name}")
            blood_type = state.context.get("required_blood_type", "Needed")
            self.logger.info(f"  Blood Type: {blood_type}")
        
        self.logger.info("-" * 70)
        self.logger.info(f"Total Estimated Time: {plan.estimated_total_time:.1f} minutes")
        self.logger.info(f"Total Distance: {plan.total_distance:.1f} km")
        self.logger.info("-" * 70)
        self.logger.info("RECOMMENDED RESOURCES:")
        if state.triage_result:
            for resource in state.triage_result.recommended_resources:
                self.logger.info(f"  - {resource}")
        self.logger.info("-" * 70)
        self.logger.info("MEDICAL PROTOCOL:")
        if plan.medical_protocol:
            self.logger.info(f"  {plan.medical_protocol.title}")
            for step in plan.medical_protocol.steps[:5]:
                self.logger.info(f"    • {step}")
        self.logger.info("=" * 70)
        self.logger.info("Awaiting coordinator approval...")
        self.logger.info("=" * 70)
    
    async def _wait_for_approval(self, state: AgentState) -> dict:
        """
        Wait for human approval (with timeout).
        
        Args:
            state: Agent state
            
        Returns:
            Approval result dictionary
        """
        # In production, this would:
        # 1. Send approval request to coordinator dashboard
        # 2. Wait for WebSocket/API callback with approval decision
        # 3. Return approval result
        
        # For this implementation, we'll check the database for approval status
        start_time = datetime.utcnow()
        
        self.logger.info(
            f"⏳ Waiting for approval (timeout: {self.approval_timeout}s)..."
        )
        
        # Check if auto-approve is enabled for testing
        if getattr(settings, "AUTO_APPROVE_CRITICAL", False):
            self.logger.warning("⚠️ AUTO-APPROVE enabled for testing")
            await asyncio.sleep(2)  # Simulate human decision time
            return {
                "approved": True,
                "approved_by": "System (Auto-Approve)",
                "notes": "Auto-approved in testing mode",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Poll for approval status
        poll_interval = 5  # Check every 5 seconds
        elapsed = 0
        
        while elapsed < self.approval_timeout:
            # Check approval status from database/cache
            approval_status = await self._check_approval_status(state.incident.incident_id)
            
            if approval_status:
                return approval_status
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            if elapsed % 30 == 0:  # Log every 30 seconds
                remaining = self.approval_timeout - elapsed
                self.logger.info(f"⏳ Still waiting for approval ({remaining}s remaining)...")
        
        # Timeout reached
        self.logger.warning(
            f"⏰ Approval timeout reached ({self.approval_timeout}s)"
        )
        
        # For critical incidents, default to rejection on timeout
        # Coordinator must explicitly approve
        return {
            "approved": False,
            "reason": f"Approval timeout ({self.approval_timeout}s elapsed)",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_approval_status(self, incident_id: str) -> Optional[dict]:
        """
        Check approval status from database or cache.
        
        Args:
            incident_id: Incident ID
            
        Returns:
            Approval result if available, None otherwise
        """
        # In production, query database for approval record:
        # SELECT * FROM incident_approvals WHERE incident_id = ?
        
        # For now, return None (no approval yet)
        return None
    
    async def request_modification(self, state: AgentState, modifications: dict) -> AgentState:
        """
        Handle plan modification requests from coordinator.
        
        Args:
            state: Current agent state
            modifications: Requested modifications
            
        Returns:
            Updated state
        """
        self.logger.info(f"🔄 Plan modification requested for {state.incident.incident_id}")
        
        # Parse modification requests
        if "hospital" in modifications:
            # Select different hospital
            hospital_rank = modifications["hospital"]
            if hospital_rank < len(state.hospitals):
                state.response_plan.selected_hospital = state.hospitals[hospital_rank]
                self.logger.info(f"  Hospital changed to: {state.hospitals[hospital_rank].name}")
        
        if "ambulance" in modifications:
            # Select different ambulance
            ambulance_rank = modifications["ambulance"]
            if ambulance_rank < len(state.ambulances):
                state.response_plan.selected_ambulance = state.ambulances[ambulance_rank]
                self.logger.info(
                    f"  Ambulance changed to: {state.ambulances[ambulance_rank].registration_number}"
                )
        
        if "notes" in modifications:
            state.approval_notes = modifications["notes"]
        
        # Recalculate plan with modifications
        # (In production, re-run PlanAgent with new selections)
        
        return state
