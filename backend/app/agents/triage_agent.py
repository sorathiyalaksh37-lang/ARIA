"""
ARIA Triage Agent
Classifies emergency severity using ML model
"""
from typing import Optional
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, TriageResult, IncidentSeverity
from app.services.ml_service import MLService


class TriageAgent(BaseAgent):
    """
    Triage Agent: Classifies incident severity.
    Uses XGBoost ML model trained on 100K incidents.
    """
    
    def __init__(self, ml_service: MLService, max_retries: int = 3):
        """
        Initialize triage agent.
        
        Args:
            ml_service: ML service instance with loaded models
            max_retries: Maximum retries on failure
        """
        super().__init__(name="TriageAgent", max_retries=max_retries)
        self.ml_service = ml_service
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Classify incident severity.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with triage_result
        """
        self._log_state_update(
            "Starting triage classification",
            incident_id=state.incident.incident_id,
            description_length=len(state.incident.description)
        )
        
        # Validate incident data
        if not state.incident.description:
            raise ValueError("Incident description is required for triage")
        
        # Prepare input for ML model
        incident_data = {
            "description": state.incident.description,
            "location": {
                "latitude": state.incident.location.latitude,
                "longitude": state.incident.location.longitude,
                "city": state.incident.location.city
            },
            "timestamp": state.incident.timestamp.isoformat(),
            "victim_count": state.incident.victim_count,
            "incident_type": state.incident.incident_type
        }
        
        # Call ML service for prediction
        self.logger.info("🔮 Calling ML model for severity prediction...")
        prediction = await self.ml_service.predict_severity(incident_data)
        
        # Map ML output to enum
        severity_map = {
            "LOW": IncidentSeverity.LOW,
            "MODERATE": IncidentSeverity.MODERATE,
            "CRITICAL": IncidentSeverity.CRITICAL
        }
        severity = severity_map.get(prediction["severity"], IncidentSeverity.MODERATE)
        
        # Determine recommended resources based on severity
        recommended_resources = self._determine_resources(severity, state.incident)
        
        # Calculate priority (1-10, where 10 is highest)
        priority = self._calculate_priority(severity, prediction["confidence"], state.incident)
        
        # Create triage result
        triage_result = TriageResult(
            severity=severity,
            confidence=prediction["confidence"],
            recommended_resources=recommended_resources,
            estimated_priority=priority
        )
        
        # Update state
        state.triage_result = triage_result
        
        # Update workflow status if critical
        if severity == IncidentSeverity.CRITICAL:
            state.requires_approval = True
            self.logger.warning(f"🚨 CRITICAL incident detected - requires approval")
        
        self._log_state_update(
            "Triage completed",
            severity=severity.value,
            confidence=f"{prediction['confidence']:.2%}",
            priority=priority
        )
        
        # Store in context for later reference
        state.context["triage_timestamp"] = datetime.utcnow().isoformat()
        state.context["triage_model_version"] = prediction.get("model_version", "1.0")
        
        return state
    
    def _determine_resources(self, severity: IncidentSeverity, incident) -> list:
        """
        Determine required resources based on severity.
        
        Args:
            severity: Classified severity
            incident: Incident information
            
        Returns:
            List of required resources
        """
        resources = ["AMBULANCE", "HOSPITAL"]
        
        if severity == IncidentSeverity.CRITICAL:
            resources.extend(["ICU", "BLOOD_BANK", "TRAUMA_TEAM"])
        elif severity == IncidentSeverity.MODERATE:
            resources.append("EMERGENCY_CARE")
        
        # Check description for specific needs
        description_lower = incident.description.lower()
        
        if any(word in description_lower for word in ["blood", "bleeding", "hemorrhage"]):
            if "BLOOD_BANK" not in resources:
                resources.append("BLOOD_BANK")
        
        if any(word in description_lower for word in ["burn", "fire", "smoke"]):
            resources.append("BURN_UNIT")
        
        if any(word in description_lower for word in ["cardiac", "heart", "chest pain"]):
            resources.append("CARDIAC_UNIT")
        
        if any(word in description_lower for word in ["stroke", "paralysis", "weakness"]):
            resources.append("STROKE_UNIT")
        
        return resources
    
    def _calculate_priority(
        self, 
        severity: IncidentSeverity, 
        confidence: float, 
        incident
    ) -> int:
        """
        Calculate incident priority (1-10).
        
        Args:
            severity: Classified severity
            confidence: Model confidence
            incident: Incident information
            
        Returns:
            Priority score (1-10)
        """
        # Base priority from severity
        base_priority = {
            IncidentSeverity.LOW: 3,
            IncidentSeverity.MODERATE: 6,
            IncidentSeverity.CRITICAL: 9
        }[severity]
        
        # Adjust for confidence
        if confidence > 0.95:
            confidence_boost = 1
        elif confidence > 0.85:
            confidence_boost = 0
        else:
            confidence_boost = -1
        
        # Adjust for victim count
        victim_boost = 0
        if incident.victim_count > 1:
            victim_boost = min(incident.victim_count - 1, 2)
        
        # Calculate final priority
        priority = base_priority + confidence_boost + victim_boost
        
        # Clamp to 1-10
        return max(1, min(10, priority))
