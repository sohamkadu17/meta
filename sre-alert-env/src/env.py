from typing import Tuple, Dict, Any, Optional
from pydantic import ValidationError
from .models import Observation, Action, Reward, State, RestartServiceAction, ClearCacheAction, ScaleUpAction, PageEngineerAction
from .tasks import get_scenario, VALID_TASK_IDS
from .grader import evaluate_step

class SREEnvironment:
    def __init__(self):
        self.state: Optional[State] = None

    def reset(self, task_id: str = "easy") -> Observation:
        """Resets the environment to the beginning of the specified task."""
        if task_id not in VALID_TASK_IDS:
            raise ValueError(f"Invalid task_id: {task_id}. Must be one of easy, medium, hard.")
        self.state = get_scenario(task_id)
        return self.state.observation

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """Takes an action and advances the environment state."""
        if not self.state:
            raise RuntimeError("Environment must be reset before taking a step.")
            
        self.state.step_count += 1
        
        # Grader handles state transitions and rewards based on the action
        reward, done = evaluate_step(self.state, action)
        
        # Max steps cutoff
        if self.state.step_count >= self.state.max_steps:
            done = True
            if reward.score == 0.0:
                reward.message += " (Max steps reached)"

        info = {
            "step_count": self.state.step_count,
            "task_id": self.state.current_task_id
        }
            
        return self.state.observation, reward, done, info
        
    def get_state(self) -> State:
        """Returns the full internal state."""
        if not self.state:
             raise RuntimeError("Environment must be reset before getting state.")
        return self.state
