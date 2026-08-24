"""
ARIA RAG Agent
Retrieves relevant medical protocols using RAG (Retrieval Augmented Generation)
"""
from typing import List, Optional
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, MedicalProtocol, IncidentSeverity
from app.core.config import settings


class RAGAgent(BaseAgent):
    """
    RAG Agent: Retrieves relevant medical protocols from knowledge base.
    Uses vector embeddings and semantic search to find relevant protocols.
    """
    
    def __init__(
        self,
        knowledge_base_path: Optional[str] = None,
        max_retries: int = 3,
        top_k: int = 3
    ):
        """
        Initialize RAG agent.
        
        Args:
            knowledge_base_path: Path to medical knowledge base
            max_retries: Maximum retries
            top_k: Number of protocols to retrieve
        """
        super().__init__(name="RAGAgent", max_retries=max_retries)
        self.knowledge_base_path = knowledge_base_path
        self.top_k = top_k
        self.vectorstore = None
        self.qa_chain = None
        
        # Initialize medical protocol database
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize medical protocol knowledge base."""
        try:
            # In production, load from vector database or file
            # For now, use in-memory protocols
            self.medical_protocols = self._get_default_protocols()
            self.logger.info(
                f"📚 Initialized knowledge base with {len(self.medical_protocols)} protocols"
            )
        except Exception as e:
            self.logger.warning(f"Failed to initialize knowledge base: {e}")
            self.medical_protocols = []
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Retrieve relevant medical protocols.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with medical protocols
        """
        self._log_state_update(
            "Starting medical protocol retrieval",
            severity=state.triage_result.severity.value if state.triage_result else "Unknown"
        )
        
        # Validate triage result
        if not state.triage_result:
            self.logger.warning("⚠️ No triage result - using default protocols")
            severity = IncidentSeverity.MODERATE
        else:
            severity = state.triage_result.severity
        
        # Build query from incident information
        query = self._build_query(state)
        
        # Retrieve relevant protocols
        relevant_protocols = await self._retrieve_protocols(
            query,
            severity,
            state.incident.incident_type
        )
        
        if not relevant_protocols:
            self.logger.warning("⚠️ No relevant protocols found - using general emergency protocol")
            relevant_protocols = [self._get_general_emergency_protocol(severity)]
        
        self.logger.info(f"📋 Retrieved {len(relevant_protocols)} relevant protocols")
        
        # Convert to MedicalProtocol objects
        protocol_objs = []
        for idx, protocol_data in enumerate(relevant_protocols, 1):
            protocol = MedicalProtocol(
                protocol_id=protocol_data["protocol_id"],
                title=protocol_data["title"],
                content=protocol_data["content"],
                severity_level=protocol_data["severity_level"],
                steps=protocol_data["steps"],
                precautions=protocol_data.get("precautions", []),
                source=protocol_data.get("source", "Medical Knowledge Base")
            )
            protocol_objs.append(protocol)
            
            self.logger.info(f"  #{idx}: {protocol.title}")
        
        # Update state
        state.medical_protocols = protocol_objs
        
        # Store in context
        if protocol_objs:
            state.context["primary_protocol"] = protocol_objs[0].title
            state.context["protocol_count"] = len(protocol_objs)
        
        self._log_state_update(
            "Protocol retrieval completed",
            protocols_found=len(protocol_objs)
        )
        
        return state
    
    def _build_query(self, state: AgentState) -> str:
        """
        Build search query from incident information.
        
        Args:
            state: Agent state
            
        Returns:
            Search query string
        """
        query_parts = [state.incident.description]
        
        if state.incident.incident_type:
            query_parts.append(state.incident.incident_type)
        
        if state.triage_result:
            query_parts.append(f"severity: {state.triage_result.severity.value}")
        
        return " ".join(query_parts)
    
    async def _retrieve_protocols(
        self,
        query: str,
        severity: IncidentSeverity,
        incident_type: Optional[str] = None
    ) -> List[dict]:
        """
        Retrieve relevant protocols using semantic search.
        
        Args:
            query: Search query
            severity: Incident severity
            incident_type: Type of incident
            
        Returns:
            List of relevant protocols
        """
        # Filter protocols by severity and type
        filtered_protocols = [
            p for p in self.medical_protocols
            if p["severity_level"] == severity or p["severity_level"] == IncidentSeverity.MODERATE
        ]
        
        if incident_type:
            type_protocols = [
                p for p in filtered_protocols
                if incident_type.upper() in p.get("applicable_types", [])
            ]
            if type_protocols:
                filtered_protocols = type_protocols
        
        # Simple keyword-based ranking (in production, use vector embeddings)
        query_lower = query.lower()
        scored_protocols = []
        
        for protocol in filtered_protocols:
            score = 0
            content_lower = protocol["content"].lower()
            title_lower = protocol["title"].lower()
            
            # Score based on keyword matches
            for word in query_lower.split():
                if len(word) > 3:  # Skip short words
                    if word in title_lower:
                        score += 3
                    if word in content_lower:
                        score += 1
            
            if score > 0:
                scored_protocols.append((score, protocol))
        
        # Sort by score and return top k
        scored_protocols.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_protocols[:self.top_k]]
    
    def _get_general_emergency_protocol(self, severity: IncidentSeverity) -> dict:
        """
        Get general emergency protocol for given severity.
        
        Args:
            severity: Incident severity
            
        Returns:
            General protocol dictionary
        """
        if severity == IncidentSeverity.CRITICAL:
            return {
                "protocol_id": "GEN-CRITICAL-001",
                "title": "Critical Emergency Response Protocol",
                "content": "Immediate life-saving interventions required",
                "severity_level": IncidentSeverity.CRITICAL,
                "steps": [
                    "Ensure scene safety",
                    "Call for immediate backup (ALS/Critical Care ambulance)",
                    "Assess ABCs (Airway, Breathing, Circulation)",
                    "Control life-threatening bleeding",
                    "Provide high-flow oxygen",
                    "Establish IV access",
                    "Monitor vital signs continuously",
                    "Prepare for rapid transport to trauma center"
                ],
                "precautions": [
                    "Do not delay transport for non-critical interventions",
                    "Maintain c-spine precautions if trauma suspected",
                    "Be prepared for rapid deterioration"
                ],
                "applicable_types": ["MEDICAL", "ACCIDENT", "VIOLENCE", "FIRE"]
            }
        elif severity == IncidentSeverity.MODERATE:
            return {
                "protocol_id": "GEN-MODERATE-001",
                "title": "Urgent Care Emergency Protocol",
                "content": "Prompt medical attention required",
                "severity_level": IncidentSeverity.MODERATE,
                "steps": [
                    "Ensure scene safety",
                    "Perform initial assessment",
                    "Stabilize patient",
                    "Provide appropriate first aid",
                    "Monitor vital signs",
                    "Transport to nearest appropriate facility"
                ],
                "precautions": [
                    "Watch for signs of deterioration",
                    "Keep patient calm and comfortable"
                ],
                "applicable_types": ["MEDICAL", "ACCIDENT", "OTHER"]
            }
        else:  # LOW
            return {
                "protocol_id": "GEN-LOW-001",
                "title": "Non-Urgent Care Protocol",
                "content": "Standard medical evaluation needed",
                "severity_level": IncidentSeverity.LOW,
                "steps": [
                    "Ensure scene safety",
                    "Assess patient condition",
                    "Provide basic first aid if needed",
                    "Arrange appropriate transport",
                    "Document incident details"
                ],
                "precautions": [
                    "Monitor for any changes in condition"
                ],
                "applicable_types": ["MEDICAL", "OTHER"]
            }
    
    def _get_default_protocols(self) -> List[dict]:
        """
        Get default medical protocols.
        
        Returns:
            List of medical protocol dictionaries
        """
        return [
            # Cardiac Emergencies
            {
                "protocol_id": "CARD-001",
                "title": "Cardiac Arrest Protocol",
                "content": "Protocol for managing cardiac arrest emergencies",
                "severity_level": IncidentSeverity.CRITICAL,
                "steps": [
                    "Confirm cardiac arrest (unresponsive, not breathing)",
                    "Start high-quality CPR immediately (100-120 compressions/min)",
                    "Attach AED/defibrillator as soon as available",
                    "Deliver shock if advised by AED",
                    "Continue CPR cycles",
                    "Establish advanced airway",
                    "Administer epinephrine every 3-5 minutes",
                    "Transport to cardiac center with ongoing resuscitation"
                ],
                "precautions": [
                    "Minimize interruptions in chest compressions",
                    "Ensure proper CPR depth (2-2.4 inches)",
                    "Rotate compressor every 2 minutes"
                ],
                "applicable_types": ["MEDICAL"],
                "source": "AHA Guidelines 2020"
            },
            # Trauma
            {
                "protocol_id": "TRAUMA-001",
                "title": "Major Trauma Protocol",
                "content": "Protocol for managing major trauma patients",
                "severity_level": IncidentSeverity.CRITICAL,
                "steps": [
                    "Ensure scene safety",
                    "Maintain c-spine immobilization",
                    "Assess and manage airway with c-spine protection",
                    "Control external hemorrhage",
                    "Assess breathing and chest injuries",
                    "Establish IV access (2 large-bore IVs)",
                    "Fluid resuscitation if hypotensive",
                    "Rapid transport to trauma center"
                ],
                "precautions": [
                    "Do not delay transport",
                    "Load and go approach for penetrating trauma",
                    "Treat for shock"
                ],
                "applicable_types": ["ACCIDENT", "VIOLENCE"],
                "source": "ATLS Guidelines"
            },
            # Stroke
            {
                "protocol_id": "STROKE-001",
                "title": "Acute Stroke Protocol",
                "content": "Protocol for suspected stroke patients",
                "severity_level": IncidentSeverity.CRITICAL,
                "steps": [
                    "Note time of symptom onset",
                    "Perform stroke assessment (FAST or CPSS)",
                    "Check blood glucose",
                    "Provide oxygen if SpO2 < 94%",
                    "Establish IV access",
                    "Perform 12-lead ECG",
                    "Alert receiving hospital (stroke alert)",
                    "Rapid transport to stroke center"
                ],
                "precautions": [
                    "Time is brain - minimize scene time",
                    "Do not give anything by mouth",
                    "Keep patient calm"
                ],
                "applicable_types": ["MEDICAL"],
                "source": "ASA Stroke Guidelines"
            },
            # Respiratory
            {
                "protocol_id": "RESP-001",
                "title": "Severe Respiratory Distress Protocol",
                "content": "Protocol for managing severe breathing difficulties",
                "severity_level": IncidentSeverity.CRITICAL,
                "steps": [
                    "Position patient for comfort (usually sitting up)",
                    "Administer high-flow oxygen",
                    "Assess for signs of respiratory failure",
                    "Prepare for assisted ventilation if needed",
                    "Obtain vital signs and SpO2",
                    "Treat underlying cause if known",
                    "Transport to appropriate facility"
                ],
                "precautions": [
                    "Monitor for deterioration",
                    "Be prepared to assist ventilation",
                    "Watch for signs of pneumothorax in trauma"
                ],
                "applicable_types": ["MEDICAL"],
                "source": "Emergency Medicine Guidelines"
            },
            # Burns
            {
                "protocol_id": "BURN-001",
                "title": "Major Burn Management Protocol",
                "content": "Protocol for managing serious burn injuries",
                "severity_level": IncidentSeverity.CRITICAL,
                "steps": [
                    "Ensure scene safety and remove from source",
                    "Stop the burning process",
                    "Assess airway for inhalation injury",
                    "Remove clothing and jewelry",
                    "Cover burns with clean, dry dressing",
                    "Establish IV access",
                    "Fluid resuscitation per Parkland formula",
                    "Transport to burn center"
                ],
                "precautions": [
                    "Do not apply ice",
                    "Do not break blisters",
                    "Watch for airway compromise",
                    "Treat for shock"
                ],
                "applicable_types": ["FIRE", "ACCIDENT"],
                "source": "Burn Treatment Guidelines"
            }
        ]
