import copy
from .models import State, Observation, ServiceState, Metrics

VALID_TASK_IDS = ("easy", "medium", "hard")

def _default_services():
    return {
        "web": ServiceState(
            service_name="web",
            metrics=Metrics(cpu_usage=0.2, memory_usage=0.3, disk_usage=0.1, latency_ms=50.0, error_count=0),
            status="healthy"
        ),
        "db": ServiceState(
            service_name="db",
            metrics=Metrics(cpu_usage=0.1, memory_usage=0.4, disk_usage=0.2, latency_ms=10.0, error_count=0),
            status="healthy"
        ),
        "cache": ServiceState(
            service_name="cache",
            metrics=Metrics(cpu_usage=0.1, memory_usage=0.1, disk_usage=0.05, latency_ms=2.0, error_count=0),
            status="healthy"
        ),
    }

def get_easy_scenario() -> State:
    services = _default_services()
    services["db"].metrics.disk_usage = 0.95
    services["db"].status = "degraded"
    
    obs = Observation(
        services=services,
        current_alert="DiskSpaceCritical on db-server-1",
        incident_severity="high",
        resolved=False
    )
    return State(current_task_id="easy", observation=obs)

def get_medium_scenario() -> State:
    services = _default_services()
    services["web"].metrics.cpu_usage = 0.99
    services["web"].metrics.latency_ms = 2500.0
    services["web"].status = "degraded"
    
    obs = Observation(
        services=services,
        current_alert="HighLatencyAPI on web cluster",
        incident_severity="medium",
        resolved=False
    )
    return State(current_task_id="medium", observation=obs)

def get_hard_scenario() -> State:
    services = _default_services()
    services["db"].status = "down"
    services["db"].metrics.latency_ms = 9999.0
    services["web"].metrics.error_count = 5000
    services["web"].status = "degraded"
    
    obs = Observation(
        services=services,
        current_alert="Frontend5xxErrors on web cluster",
        incident_severity="critical",
        resolved=False
    )
    return State(current_task_id="hard", observation=obs)

def get_scenario(task_id: str) -> State:
    scenarios = {
        "easy": get_easy_scenario,
        "medium": get_medium_scenario,
        "hard": get_hard_scenario
    }
    if task_id not in scenarios:
        raise ValueError(f"Invalid task_id: {task_id}. Must be one of easy, medium, hard.")
    return scenarios[task_id]()
