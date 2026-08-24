"""
ARIA Plan Agent
Generates comprehensive response plan from all agent outputs
"""
from datetime import datetime
from typing import List

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, ResponsePlan, WorkflowStatus
from app.core.config import settings


class PlanAgent(BaseAgent):
    """
    Plan Agent: Synthesizes all agent outputs into a comprehensive response plan.
    Creates actionable steps and estimates for emergency response.
    """
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize plan agent.
        
        Args:
            max_retries: Maximum retries
        """
        super().__init__(name="PlanAgent", max_retries=max_retries)
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Generate comprehensive response plan.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with response plan
        """
        self._log_state_update(
            "Starting response plan generation",
            incident_id=state.incident.incident_id
        )
        
        # Validate all required data is present
        self._validate_plan_inputs(state)
        
        # Select best resources
        selected_hospital = state.hospitals[0] if state.hospitals else None
        selected_ambulance = state.ambulances[0] if state.ambulances else None
        selected_blood_bank = state.blood_banks[0] if state.blood_banks else None
        
        # Calculate total time and distance
        total_time, total_distance = self._calculate_totals(state)
        
        # Generate action steps
        action_steps = self._generate_action_steps(state)
        
        # Create response plan
        plan_id = f"PLAN-{state.incident.incident_id}-{int(datetime.utcnow().timestamp())}"
        
        response_plan = ResponsePlan(
            plan_id=plan_id,
            incident_id=state.incident.incident_id,
            severity=state.triage_result.severity,
            selected_hospital=selected_hospital,
            selected_ambulance=selected_ambulance,
            selected_blood_bank=selected_blood_bank,
            route=state.route,
            medical_protocol=state.medical_protocols[0] if state.medical_protocols else None,
            estimated_total_time=total_time,
            total_distance=total_distance,
            action_steps=action_steps,
            notifications_sent=[],  # Will be populated by Communication Agent
            created_at=datetime.utcnow()
        )
        
        # Update state
        state.response_plan = response_plan
        state.workflow_status = WorkflowStatus.AWAITING_APPROVAL
        
        # Log plan summary
        self._log_plan_summary(response_plan)
        
        self._log_state_update(
            "Response plan generated",
            plan_id=plan_id,
            total_time=f"{total_time:.1f} min",
            total_distance=f"{total_distance:.1f} km",
            action_steps=len(action_steps)
        )
        
        return state
    
    def _validate_plan_inputs(self, state: AgentState):
        """
        Validate that all required data is present.
        
        Args:
            state: Agent state
            
        Raises:
            ValueError: If required data is missing
        """
        if not state.triage_result:
            raise ValueError("Triage result is required for plan generation")
        
        if not state.hospitals:
            raise ValueError("At least one hospital is required for plan generation")
        
        if not state.ambulances:
            raise ValueError("At least one ambulance is required for plan generation")
    
    def _calculate_totals(self, state: AgentState) -> tuple:
        """
        Calculate total time and distance for response.
        
        Args:
            state: Agent state
            
        Returns:
            Tuple of (total_time_minutes, total_distance_km)
        """
        total_time = 0
        total_distance = 0
        
        # Ambulance ETA to incident
        if state.ambulances:
            total_time += state.ambulances[0].eta_minutes
            total_distance += state.ambulances[0].distance_km
        
        # Transport time from incident to hospital
        if state.route:
            # Route includes both segments, so we use it directly
            total_time = state.route.eta_minutes
            total_distance = state.route.distance_km
        elif state.hospitals:
            # Fallback: add hospital distance
            total_time += state.hospitals[0].eta_minutes or 0
            total_distance += state.hospitals[0].distance_km
        
        # Add time for patient pickup and handoff
        total_time += 5  # 5 minutes for patient pickup
        total_time += 3  # 3 minutes for hospital handoff
        
        # Add blood bank detour if needed
        if state.blood_banks:
            # Simplified: add 10 minutes for blood pickup
            total_time += 10
        
        return total_time, total_distance
    
    def _generate_action_steps(self, state: AgentState) -> List[str]:
        """
        Generate ordered list of action steps.
        
        Args:
            state: Agent state
            
        Returns:
            List of action step descriptions
        """
        steps = []
        
        # Step 1: Dispatch
        if state.ambulances:
            amb = state.ambulances[0]
            steps.append(
                f"1. DISPATCH: {amb.registration_number} ({amb.ambulance_type}) "
                f"from current location to incident site"
            )
            steps.append(
                f"   - ETA to incident: {amb.eta_minutes:.1f} minutes"
            )
            steps.append(
                f"   - Distance: {amb.distance_km:.1f} km"
            )
        
        # Step 2: Medical Protocol
        if state.medical_protocols:
            protocol = state.medical_protocols[0]
            steps.append(f"2. MEDICAL PROTOCOL: {protocol.title}")
            for idx, step in enumerate(protocol.steps[:5], 1):
                steps.append(f"   {idx}. {step}")
        
        # Step 3: Blood Arrangement (if needed)
        if state.blood_banks:
            bb = state.blood_banks[0]
            blood_type = state.context.get("required_blood_type", "Required type")
            steps.append(
                f"3. BLOOD ARRANGEMENT: Contact {bb.name} "
                f"({bb.distance_km:.1f}km away)"
            )
            steps.append(f"   - Blood type: {blood_type}")
            steps.append(f"   - Contact: {bb.contact_phone}")
        
        # Step 4: Hospital Preparation
        if state.hospitals:
            hosp = state.hospitals[0]
            steps.append(
                f"4. HOSPITAL ALERT: Notify {hosp.name} "
                f"({hosp.distance_km:.1f}km from incident)"
            )
            steps.append(f"   - Severity: {state.triage_result.severity.value}")
            steps.append(f"   - Available beds: {hosp.available_beds}")
            steps.append(f"   - Available ICU beds: {hosp.available_icu_beds}")
            steps.append(f"   - Contact: {hosp.contact_phone}")
        
        # Step 5: Transport
        if state.route:
            steps.append(
                f"5. TRANSPORT: Follow optimized route to {state.hospitals[0].name}"
            )
            steps.append(f"   - Total distance: {state.route.distance_km:.1f} km")
            steps.append(f"   - Estimated time: {state.route.eta_minutes:.1f} minutes")
            steps.append(f"   - Traffic level: {state.route.traffic_level}")
        
        # Step 6: Handoff
        steps.append("6. HOSPITAL HANDOFF: Transfer patient to emergency department")
        steps.append("   - Brief emergency team on patient condition")
        steps.append("   - Provide all medical intervention details")
        steps.append("   - Complete transfer documentation")
        
        # Step 7: Follow-up
        steps.append("7. POST-INCIDENT: Complete incident documentation")
        steps.append("   - Update ambulance status")
        steps.append("   - Record response times")
        steps.append("   - Document any issues or delays")
        
        return steps
    
    def _log_plan_summary(self, plan: ResponsePlan):
        """
        Log detailed plan summary.
        
        Args:
            plan: Response plan
        """
        self.logger.info("=" * 60)
        self.logger.info("📋 RESPONSE PLAN SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Plan ID: {plan.plan_id}")
        self.logger.info(f"Incident ID: {plan.incident_id}")
        self.logger.info(f"Severity: {plan.severity.value}")
        self.logger.info("-" * 60)
        
        if plan.selected_ambulance:
            self.logger.info(
                f"Ambulance: {plan.selected_ambulance.registration_number} "
                f"({plan.selected_ambulance.ambulance_type})"
            )
            self.logger.info(f"  ETA: {plan.selected_ambulance.eta_minutes:.1f} min")
        
        if plan.selected_hospital:
            self.logger.info(f"Hospital: {plan.selected_hospital.name}")
            self.logger.info(
                f"  Distance: {plan.selected_hospital.distance_km:.1f} km, "
                f"Score: {plan.selected_hospital.suitability_score:.3f}"
            )
        
        if plan.selected_blood_bank:
            self.logger.info(f"Blood Bank: {plan.selected_blood_bank.name}")
            self.logger.info(f"  Distance: {plan.selected_blood_bank.distance_km:.1f} km")
        
        self.logger.info("-" * 60)
        self.logger.info(f"Total Distance: {plan.total_distance:.1f} km")
        self.logger.info(f"Total Estimated Time: {plan.estimated_total_time:.1f} minutes")
        self.logger.info("-" * 60)
        self.logger.info(f"Action Steps: {len(plan.action_steps)}")
        self.logger.info("=" * 60)
