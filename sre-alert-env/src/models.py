from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict

ServiceType = Literal["web", "db", "cache"]
Severity = Literal["low", "medium", "high", "critical"]

class Metrics(BaseModel):
    cpu_usage: float = Field(..., ge=0.0, le=1.0, description="CPU utilization (0.0 - 1.0)")
    memory_usage: float = Field(..., ge=0.0, le=1.0, description="Memory utilization (0.0 - 1.0)")
    disk_usage: float = Field(..., ge=0.0, le=1.0, description="Disk utilization (0.0 - 1.0)")
    latency_ms: float = Field(..., ge=0.0, description="Latency in milliseconds")
    error_count: int = Field(..., ge=0, description="Number of errors in the last polling window")

class ServiceState(BaseModel):
    service_name: ServiceType
    metrics: Metrics
    status: Literal["healthy", "degraded", "down"]

class Observation(BaseModel):
    services: Dict[ServiceType, ServiceState]
    current_alert: Optional[str] = Field(None, description="Active alert description, if any")
    incident_severity: Optional[Severity] = Field(None, description="Incident severity level")
    resolved: bool = Field(False, description="Whether the incident has been successfully resolved")

# We use a discriminated union for actions to make it strongly typed
class RestartServiceAction(BaseModel):
    action_type: Literal["restart_service"] = "restart_service"
    service_name: ServiceType

class ScaleUpAction(BaseModel):
    action_type: Literal["scale_up"] = "scale_up"
    cluster_name: ServiceType
    node_count: int = Field(..., gt=0)

class ClearCacheAction(BaseModel):
    action_type: Literal["clear_cache"] = "clear_cache"
    server_id: str

class PageEngineerAction(BaseModel):
    action_type: Literal["page_engineer"] = "page_engineer"
    team_name: str

Action = RestartServiceAction | ScaleUpAction | ClearCacheAction | PageEngineerAction

class Reward(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Task score (1.0 for success)")
    dense_reward: float = Field(..., description="Intermediate continuous reward for RL/scoring")
    message: str = Field(..., description="Feedback message explaining the reward")

class State(BaseModel):
    """Internal environment state."""
    current_task_id: str
    step_count: int = 0
    max_steps: int = 10
    observation: Observation
