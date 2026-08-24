"""
ARIA Monitoring Agent
Tracks system health, performance, and agent execution
"""
import time
import psutil
from typing import Dict, Any, List
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, WorkflowStatus


class MonitoringAgent(BaseAgent):
    """
    Monitoring Agent: Tracks system health and agent performance.
    Collects metrics for observability and alerting.
    """
    
    def __init__(self, max_retries: int = 1):
        """
        Initialize monitoring agent.
        
        Args:
            max_retries: Maximum retries (monitoring failures should not block workflow)
        """
        super().__init__(name="MonitoringAgent", max_retries=max_retries)
        self.start_time = None
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Collect monitoring metrics and health status.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with monitoring data
        """
        self._log_state_update(
            "Starting system monitoring",
            incident_id=state.incident.incident_id
        )
        
        try:
            # Collect workflow metrics
            workflow_metrics = self._collect_workflow_metrics(state)
            
            # Collect system health
            system_health = self._collect_system_health()
            
            # Collect agent performance
            agent_performance = self._collect_agent_performance(state)
            
            # Calculate SLAs
            sla_status = self._calculate_sla_status(state, workflow_metrics)
            
            # Combine all monitoring data
            monitoring_data = {
                "workflow_metrics": workflow_metrics,
                "system_health": system_health,
                "agent_performance": agent_performance,
                "sla_status": sla_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in context
            state.context["monitoring"] = monitoring_data
            
            # Log summary
            self._log_monitoring_summary(monitoring_data)
            
            # Check for alerts
            alerts = self._check_alerts(monitoring_data)
            if alerts:
                state.context["monitoring_alerts"] = alerts
                for alert in alerts:
                    self.logger.warning(f"⚠️ ALERT: {alert}")
            
            self._log_state_update(
                "Monitoring completed",
                alerts=len(alerts),
                sla_met=sla_status["overall_sla_met"]
            )
            
        except Exception as e:
            # Monitoring failures should not stop workflow
            self.logger.error(f"Monitoring failed: {e}")
            state.context["monitoring_error"] = str(e)
        
        return state
    
    def _collect_workflow_metrics(self, state: AgentState) -> Dict[str, Any]:
        """
        Collect workflow execution metrics.
        
        Args:
            state: Agent state
            
        Returns:
            Workflow metrics dictionary
        """
        # Calculate elapsed time
        if state.created_at:
            elapsed_seconds = (datetime.utcnow() - state.created_at).total_seconds()
        else:
            elapsed_seconds = 0
        
        # Count agents
        total_agents = 9  # Fixed number of agents in workflow
        completed_agents = len(state.completed_agents)
        failed_agents = len(state.failed_agents)
        pending_agents = total_agents - completed_agents - failed_agents
        
        return {
            "incident_id": state.incident.incident_id,
            "workflow_status": state.workflow_status.value,
            "elapsed_time_seconds": round(elapsed_seconds, 2),
            "total_agents": total_agents,
            "completed_agents": completed_agents,
            "failed_agents": failed_agents,
            "pending_agents": pending_agents,
            "completion_percentage": round((completed_agents / total_agents) * 100, 1),
            "error_count": len(state.errors),
            "retry_count": state.retry_count,
            "requires_approval": state.requires_approval,
            "severity": state.triage_result.severity.value if state.triage_result else "Unknown"
        }
    
    def _collect_system_health(self) -> Dict[str, Any]:
        """
        Collect system health metrics.
        
        Returns:
            System health dictionary
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            return {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory_percent, 1),
                "memory_available_mb": round(memory_available_mb, 1),
                "disk_percent": round(disk_percent, 1),
                "disk_free_gb": round(disk_free_gb, 2),
                "status": self._determine_health_status(cpu_percent, memory_percent, disk_percent)
            }
        except Exception as e:
            self.logger.warning(f"Failed to collect system health: {e}")
            return {"status": "unknown", "error": str(e)}
    
    def _collect_agent_performance(self, state: AgentState) -> Dict[str, Any]:
        """
        Collect agent performance metrics.
        
        Args:
            state: Agent state
            
        Returns:
            Agent performance dictionary
        """
        agent_stats = {}
        
        # Analyze errors by agent
        errors_by_agent = {}
        for error in state.errors:
            agent_name = error.agent_name
            if agent_name not in errors_by_agent:
                errors_by_agent[agent_name] = 0
            errors_by_agent[agent_name] += 1
        
        # Performance summary
        for agent_name in state.completed_agents:
            agent_stats[agent_name] = {
                "status": "completed",
                "errors": errors_by_agent.get(agent_name, 0)
            }
        
        for agent_name in state.failed_agents:
            agent_stats[agent_name] = {
                "status": "failed",
                "errors": errors_by_agent.get(agent_name, 0)
            }
        
        return {
            "agent_stats": agent_stats,
            "total_errors": len(state.errors),
            "failed_agents_list": state.failed_agents
        }
    
    def _calculate_sla_status(self, state: AgentState, workflow_metrics: dict) -> Dict[str, Any]:
        """
        Calculate SLA compliance status.
        
        Args:
            state: Agent state
            workflow_metrics: Workflow metrics
            
        Returns:
            SLA status dictionary
        """
        elapsed_seconds = workflow_metrics["elapsed_time_seconds"]
        
        # Define SLAs based on severity
        if state.triage_result:
            severity = state.triage_result.severity.value
            sla_targets = {
                "CRITICAL": {"response_time": 180, "completion_time": 600},  # 3 min, 10 min
                "MODERATE": {"response_time": 300, "completion_time": 900},  # 5 min, 15 min
                "LOW": {"response_time": 600, "completion_time": 1800}       # 10 min, 30 min
            }
            sla = sla_targets.get(severity, sla_targets["MODERATE"])
        else:
            sla = {"response_time": 300, "completion_time": 900}
        
        # Check response time (time to generate plan)
        response_time_met = False
        if state.response_plan:
            plan_time = (state.response_plan.created_at - state.created_at).total_seconds()
            response_time_met = plan_time <= sla["response_time"]
        
        # Check completion time (time to dispatch)
        completion_time_met = False
        if state.workflow_status in [WorkflowStatus.DISPATCHED, WorkflowStatus.COMPLETED]:
            completion_time_met = elapsed_seconds <= sla["completion_time"]
        
        return {
            "severity": state.triage_result.severity.value if state.triage_result else "Unknown",
            "sla_response_time": sla["response_time"],
            "sla_completion_time": sla["completion_time"],
            "actual_elapsed_time": elapsed_seconds,
            "response_time_met": response_time_met,
            "completion_time_met": completion_time_met,
            "overall_sla_met": response_time_met and completion_time_met
        }
    
    def _determine_health_status(
        self,
        cpu_percent: float,
        memory_percent: float,
        disk_percent: float
    ) -> str:
        """
        Determine overall system health status.
        
        Args:
            cpu_percent: CPU usage percentage
            memory_percent: Memory usage percentage
            disk_percent: Disk usage percentage
            
        Returns:
            Health status: "healthy", "degraded", or "critical"
        """
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            return "critical"
        elif cpu_percent > 75 or memory_percent > 75 or disk_percent > 85:
            return "degraded"
        else:
            return "healthy"
    
    def _check_alerts(self, monitoring_data: dict) -> List[str]:
        """
        Check for alerting conditions.
        
        Args:
            monitoring_data: Monitoring data
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        # Check system health
        system_health = monitoring_data["system_health"]
        if system_health.get("status") == "critical":
            alerts.append(
                f"System resources critical: CPU {system_health.get('cpu_percent')}%, "
                f"Memory {system_health.get('memory_percent')}%"
            )
        elif system_health.get("status") == "degraded":
            alerts.append(
                f"System resources degraded: CPU {system_health.get('cpu_percent')}%, "
                f"Memory {system_health.get('memory_percent')}%"
            )
        
        # Check workflow errors
        workflow_metrics = monitoring_data["workflow_metrics"]
        if workflow_metrics["failed_agents"] > 0:
            alerts.append(
                f"{workflow_metrics['failed_agents']} agent(s) failed during execution"
            )
        
        if workflow_metrics["error_count"] > 3:
            alerts.append(
                f"High error count: {workflow_metrics['error_count']} errors"
            )
        
        # Check SLA
        sla_status = monitoring_data["sla_status"]
        if not sla_status["response_time_met"]:
            alerts.append(
                f"Response time SLA violated: {sla_status['actual_elapsed_time']:.1f}s "
                f"(target: {sla_status['sla_response_time']}s)"
            )
        
        return alerts
    
    def _log_monitoring_summary(self, monitoring_data: dict):
        """
        Log monitoring summary.
        
        Args:
            monitoring_data: Monitoring data
        """
        self.logger.info("=" * 60)
        self.logger.info("📊 MONITORING SUMMARY")
        self.logger.info("=" * 60)
        
        # Workflow metrics
        wf = monitoring_data["workflow_metrics"]
        self.logger.info(f"Workflow Status: {wf['workflow_status']}")
        self.logger.info(f"Elapsed Time: {wf['elapsed_time_seconds']:.2f}s")
        self.logger.info(
            f"Agents: {wf['completed_agents']}/{wf['total_agents']} completed "
            f"({wf['completion_percentage']}%)"
        )
        if wf['failed_agents'] > 0:
            self.logger.warning(f"Failed Agents: {wf['failed_agents']}")
        if wf['error_count'] > 0:
            self.logger.warning(f"Errors: {wf['error_count']}")
        
        # System health
        sh = monitoring_data["system_health"]
        self.logger.info("-" * 60)
        self.logger.info(f"System Health: {sh.get('status', 'unknown').upper()}")
        self.logger.info(
            f"  CPU: {sh.get('cpu_percent', 0)}%, "
            f"Memory: {sh.get('memory_percent', 0)}%, "
            f"Disk: {sh.get('disk_percent', 0)}%"
        )
        
        # SLA status
        sla = monitoring_data["sla_status"]
        self.logger.info("-" * 60)
        self.logger.info(f"SLA Status: {'✅ MET' if sla['overall_sla_met'] else '❌ VIOLATED'}")
        self.logger.info(
            f"  Response Time: {sla['actual_elapsed_time']:.1f}s "
            f"(target: {sla['sla_response_time']}s) "
            f"{'✅' if sla['response_time_met'] else '❌'}"
        )
        
        self.logger.info("=" * 60)
