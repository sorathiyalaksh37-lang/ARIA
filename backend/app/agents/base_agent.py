"""
ARIA Base Agent
Abstract base class for all LangGraph agents
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from app.agents.state import AgentState, AgentError, WorkflowStatus

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all ARIA agents.
    Provides common functionality: logging, error handling, retries, timing.
    """
    
    def __init__(self, name: str, max_retries: int = 3):
        """
        Initialize base agent.
        
        Args:
            name: Agent name
            max_retries: Maximum number of retries on failure
        """
        self.name = name
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"agents.{name}")
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute agent with error handling and retries.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        start_time = time.time()
        self.logger.info(f"🤖 {self.name} starting execution")
        
        # Update state
        state.current_agent = self.name
        state.updated_at = datetime.utcnow()
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                # Execute agent logic
                state = await self.run(state)
                
                # Mark as completed
                if self.name not in state.completed_agents:
                    state.completed_agents.append(self.name)
                
                execution_time = time.time() - start_time
                self.logger.info(
                    f"✅ {self.name} completed successfully in {execution_time:.2f}s"
                )
                
                state.updated_at = datetime.utcnow()
                return state
                
            except Exception as e:
                last_error = e
                retry_count += 1
                
                self.logger.error(
                    f"❌ {self.name} failed (attempt {retry_count}/{self.max_retries + 1}): {str(e)}"
                )
                
                # Record error
                error = AgentError(
                    agent_name=self.name,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    retry_count=retry_count
                )
                state.errors.append(error)
                
                if retry_count <= self.max_retries:
                    self.logger.info(f"🔄 Retrying {self.name}...")
                    await self._wait_before_retry(retry_count)
                else:
                    # Max retries exceeded
                    self.logger.error(f"💥 {self.name} failed after {self.max_retries} retries")
                    state.failed_agents.append(self.name)
                    state.workflow_status = WorkflowStatus.FAILED
                    break
        
        execution_time = time.time() - start_time
        state.updated_at = datetime.utcnow()
        
        return state
    
    @abstractmethod
    async def run(self, state: AgentState) -> AgentState:
        """
        Main agent logic. Must be implemented by subclasses.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        pass
    
    async def _wait_before_retry(self, retry_count: int):
        """
        Exponential backoff before retry.
        
        Args:
            retry_count: Current retry count
        """
        import asyncio
        wait_time = min(2 ** retry_count, 30)  # Max 30 seconds
        self.logger.info(f"⏳ Waiting {wait_time}s before retry...")
        await asyncio.sleep(wait_time)
    
    def _log_state_update(self, message: str, **kwargs):
        """Log state update with context."""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.logger.info(f"📝 {self.name}: {message} | {context}")
    
    def _validate_state(self, state: AgentState, required_fields: list) -> bool:
        """
        Validate state has required fields.
        
        Args:
            state: Agent state
            required_fields: List of required field names
            
        Returns:
            True if valid, False otherwise
        """
        for field in required_fields:
            if not hasattr(state, field) or getattr(state, field) is None:
                self.logger.error(f"❌ Missing required field: {field}")
                return False
        return True
