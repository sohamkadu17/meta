from typing import Tuple
from .models import State, Action, Reward, RestartServiceAction, ClearCacheAction, ScaleUpAction, PageEngineerAction

def evaluate_step(state: State, action: Action) -> Tuple[Reward, bool]:
    task_id = state.current_task_id
    done = False
    
    score = 0.0
    dense_reward = -0.05 # slight penalty for every step to encourage efficiency
    message = "Action executed."
    
    if task_id == "easy":
        if isinstance(action, ClearCacheAction) and action.server_id == "db-server-1":
            state.observation.resolved = True
            state.observation.services["db"].metrics.disk_usage = 0.1
            state.observation.services["db"].status = "healthy"
            score = 1.0
            dense_reward = 1.0
            message = "Cache cleared on DB. Disk usage normalized. Issue resolved."
            done = True
        elif isinstance(action, RestartServiceAction) and action.service_name == "db":
            state.observation.resolved = True
            state.observation.services["db"].metrics.disk_usage = 0.1
            state.observation.services["db"].status = "healthy"
            score = 1.0
            dense_reward = 1.0
            message = "DB restarted. Temp files cleared. Issue resolved."
            done = True
        else:
            dense_reward -= 0.5
            message = "Incorrect action. DB disk is still full."

    elif task_id == "medium":
        if isinstance(action, ScaleUpAction) and action.cluster_name == "web":
            if action.node_count == 3:
                state.observation.resolved = True
                state.observation.services["web"].metrics.cpu_usage = 0.3
                state.observation.services["web"].metrics.latency_ms = 40.0
                state.observation.services["web"].status = "healthy"
                score = 1.0
                dense_reward = 1.0
                message = "Web cluster scaled by exactly 3 nodes. Latency normalized. Issue resolved."
                done = True
            elif action.node_count in (1, 2):
                state.observation.services["web"].metrics.cpu_usage = 0.75
                state.observation.services["web"].metrics.latency_ms = 1200.0
                state.observation.services["web"].status = "degraded"
                score = 0.5
                dense_reward = 0.25
                message = "Partial mitigation: scale-up helped, but capacity is still insufficient."
            elif action.node_count > 5:
                state.observation.services["web"].status = "degraded"
                score = 0.0
                dense_reward = -0.5
                message = "Over-scaling detected. Resource waste penalty applied; incident not resolved."
            else:
                state.observation.resolved = True
                state.observation.services["web"].metrics.cpu_usage = 0.35
                state.observation.services["web"].metrics.latency_ms = 55.0
                state.observation.services["web"].status = "healthy"
                score = 0.7
                dense_reward = 0.4
                message = f"Issue resolved with suboptimal scaling ({action.node_count} nodes)."
                done = True
        else:
            dense_reward -= 0.5
            message = "Wrong action. Web is still overloaded."
            
    elif task_id == "hard":
        if isinstance(action, RestartServiceAction) and action.service_name == "db":
            dense_reward += 0.5
            message = "DB restarted. It is recovering, but DB team needs to be involved to prevent data corruption."
            state.observation.services["db"].status = "degraded"
        elif isinstance(action, PageEngineerAction) and action.team_name == "db-team":
            if state.observation.services["db"].status == "degraded":
                score = 1.0
                dense_reward = 1.0
                state.observation.resolved = True
                state.observation.services["db"].status = "healthy"
                state.observation.services["db"].metrics.latency_ms = 15.0
                state.observation.services["web"].metrics.error_count = 0
                state.observation.services["web"].status = "healthy"
                message = "DB team paged after restart. They stabilized the DB. Frontend errors resolved. Issue fixed."
                done = True
            else:
                dense_reward += 0.2
                message = "DB team paged. They say the DB needs a restart to recover."
        else:
            dense_reward -= 0.5
            message = "Incorrect action. DB is still down and frontend is failing."
            
    if state.observation.resolved:
        state.observation.current_alert = None
        state.observation.incident_severity = "low"

    return Reward(score=score, dense_reward=dense_reward, message=message), done
