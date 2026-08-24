"""
ARIA Agent Orchestrator
Coordinates all 9 agents using LangGraph workflow
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langchain.schema import Document

from app.agents.state import AgentState, WorkflowStatus, IncidentInfo
from app.agents.triage_agent import TriageAgent
from app.agents.hospital_agent import HospitalAgent
from app.agents.ambulance_agent import AmbulanceAgent
from app.agents.blood_agent import BloodAgent
from app.agents.route_agent import RouteAgent
from app.agents.rag_agent import RAGAgent
from app.agents.plan_agent import PlanAgent
from app.agents.communication_agent import CommunicationAgent
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.monitoring_agent import MonitoringAgent

from app.services.ml_service import MLService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates all 9 agents in a LangGraph workflow.
    Manages parallel execution, conditional routing, and human-in-the-loop.
    """
    
    def __init__(
        self,
        ml_service: MLService,
        db_session: AsyncSession
    ):
        """
        Initialize agent orchestrator.
        
        Args:
            ml_service: ML service instance
            db_session: Database session
        """
        self.ml_service = ml_service
        self.db = db_session
        
        # Initialize all agents
        self.triage_agent = TriageAgent(ml_service=ml_service)
        self.hospital_agent = HospitalAgent(ml_service=ml_service, db_session=db_session)
        self.ambulance_agent = AmbulanceAgent(ml_service=ml_service, db_session=db_session)
        self.blood_agent = BloodAgent(db_session=db_session)
        self.route_agent = RouteAgent()
        self.rag_agent = RAGAgent()
        self.plan_agent = PlanAgent()
        self.communication_agent = CommunicationAgent()
        self.coordinator_agent = CoordinatorAgent()
        self.monitoring_agent = MonitoringAgent()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info("🤖 Agent Orchestrator initialized with 9 agents")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow with all agents.
        
        Returns:
            StateGraph workflow
        """
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("triage", self._triage_node)
        workflow.add_node("parallel_search", self._parallel_search_node)
        workflow.add_node("route", self._route_node)
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("communication", self._communication_node)
        workflow.add_node("monitoring", self._monitoring_node)
        
        # Define workflow edges
        # 1. Start -> Triage
        workflow.set_entry_point("triage")
        
        # 2. Triage -> Parallel Search (Hospital + Ambulance + Blood + RAG)
        workflow.add_edge("triage", "parallel_search")
        
        # 3. Parallel Search -> Route
        workflow.add_edge("parallel_search", "route")
        
        # 4. Route -> Plan
        workflow.add_edge("route", "plan")
        
        # 5. Plan -> Coordinator (conditional: only if approval required)
        workflow.add_conditional_edges(
            "plan",
            self._should_require_approval,
            {
                "approve": "coordinator",
                "skip": "communication"
            }
        )
        
        # 6. Coordinator -> Communication (conditional: only if approved)
        workflow.add_conditional_edges(
            "coordinator",
            self._is_approved,
            {
                "approved": "communication",
                "rejected": "monitoring"  # Skip communication if rejected
            }
        )
        
        # 7. Communication -> Monitoring
        workflow.add_edge("communication", "monitoring")
        
        # 8. Monitoring -> End
        workflow.add_edge("monitoring", END)
        
        return workflow.compile()
    
    async def execute(self, incident: IncidentInfo) -> AgentState:
        """
        Execute the complete agent workflow for an incident.
        
        Args:
            incident: Incident information
            
        Returns:
            Final agent state with complete response plan
        """
        logger.info("=" * 80)
        logger.info(f"🚀 Starting ARIA Agent Workflow for Incident: {incident.incident_id}")
        logger.info("=" * 80)
        
        # Initialize state
        initial_state = AgentState(
            incident=incident,
            workflow_status=WorkflowStatus.IN_PROGRESS,
            created_at=datetime.utcnow()
        )
        
        try:
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Log completion
            elapsed = (datetime.utcnow() - initial_state.created_at).total_seconds()
            logger.info("=" * 80)
            logger.info(
                f"✅ Workflow completed in {elapsed:.2f}s - "
                f"Status: {final_state.workflow_status.value}"
            )
            logger.info("=" * 80)
            
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            initial_state.workflow_status = WorkflowStatus.FAILED
            initial_state.errors.append({
                "agent_name": "Orchestrator",
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            return initial_state
    
    # ========== Agent Nodes ==========
    
    async def _triage_node(self, state: AgentState) -> AgentState:
        """Execute triage agent."""
        logger.info("🔍 Executing Triage Agent...")
        return await self.triage_agent.execute(state)
    
    async def _parallel_search_node(self, state: AgentState) -> AgentState:
        """Execute Hospital, Ambulance, Blood, and RAG agents in parallel."""
        logger.info("🔄 Executing Parallel Search (Hospital + Ambulance + Blood + RAG)...")
        
        # Run agents in parallel
        tasks = [
            self.hospital_agent.execute(state),
            self.ambulance_agent.execute(state),
            self.blood_agent.execute(state),
            self.rag_agent.execute(state)
        ]
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results (all agents update the same state object)
        # The last successful update wins for each field
        merged_state = state
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_names = ["HospitalAgent", "AmbulanceAgent", "BloodAgent", "RAGAgent"]
                logger.error(f"❌ {agent_names[i]} failed: {result}")
            else:
                merged_state = result  # Use latest state
        
        return merged_state
    
    async def _route_node(self, state: AgentState) -> AgentState:
        """Execute route agent."""
        logger.info("🗺️ Executing Route Agent...")
        return await self.route_agent.execute(state)
    
    async def _plan_node(self, state: AgentState) -> AgentState:
        """Execute plan agent."""
        logger.info("📋 Executing Plan Agent...")
        return await self.plan_agent.execute(state)
    
    async def _coordinator_node(self, state: AgentState) -> AgentState:
        """Execute coordinator agent."""
        logger.info("👤 Executing Coordinator Agent (Human-in-the-Loop)...")
        return await self.coordinator_agent.execute(state)
    
    async def _communication_node(self, state: AgentState) -> AgentState:
        """Execute communication agent."""
        logger.info("📡 Executing Communication Agent...")
        return await self.communication_agent.execute(state)
    
    async def _monitoring_node(self, state: AgentState) -> AgentState:
        """Execute monitoring agent."""
        logger.info("📊 Executing Monitoring Agent...")
        state = await self.monitoring_agent.execute(state)
        
        # Set final workflow status
        if state.workflow_status == WorkflowStatus.APPROVED:
            state.workflow_status = WorkflowStatus.COMPLETED
        
        return state
    
    # ========== Conditional Routing Functions ==========
    
    def _should_require_approval(self, state: AgentState) -> str:
        """Check if human approval is required."""
        if state.requires_approval:
            return "approve"
        else:
            return "skip"
    
    def _is_approved(self, state: AgentState) -> str:
        """Check if plan was approved."""
        if state.workflow_status == WorkflowStatus.APPROVED:
            return "approved"
        else:
            return "rejected"
    
    # ========== Helper Methods ==========
    
    async def get_workflow_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current workflow status for an incident.
        
        Args:
            incident_id: Incident ID
            
        Returns:
            Workflow status dictionary
        """
        # In production, query from database or cache
        # For now, return None
        return None
    
    async def approve_plan(self, incident_id: str, approved_by: str, notes: Optional[str] = None):
        """
        Approve a response plan.
        
        Args:
            incident_id: Incident ID
            approved_by: Approver name/ID
            notes: Optional approval notes
        """
        # In production, update database with approval
        logger.info(f"✅ Plan approved for {incident_id} by {approved_by}")
        # Store in database: INSERT INTO incident_approvals ...
    
    async def reject_plan(self, incident_id: str, rejected_by: str, reason: str):
        """
        Reject a response plan.
        
        Args:
            incident_id: Incident ID
            rejected_by: Rejector name/ID
            reason: Rejection reason
        """
        # In production, update database with rejection
        logger.info(f"❌ Plan rejected for {incident_id} by {rejected_by}: {reason}")
        # Store in database: INSERT INTO incident_rejections ...
    
    async def modify_plan(
        self,
        incident_id: str,
        modifications: Dict[str, Any],
        modified_by: str
    ):
        """
        Request plan modifications.
        
        Args:
            incident_id: Incident ID
            modifications: Requested modifications
            modified_by: Modifier name/ID
        """
        logger.info(f"🔄 Plan modification requested for {incident_id} by {modified_by}")
        # Store in database and trigger re-execution of affected agents


# ========== Convenience Functions ==========

async def create_orchestrator(
    ml_service: MLService,
    db_session: AsyncSession
) -> AgentOrchestrator:
    """
    Create and initialize agent orchestrator.
    
    Args:
        ml_service: ML service instance
        db_session: Database session
        
    Returns:
        Initialized orchestrator
    """
    orchestrator = AgentOrchestrator(ml_service=ml_service, db_session=db_session)
    logger.info("✅ Agent Orchestrator created successfully")
    return orchestrator
