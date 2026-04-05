import os
from typing import Any, Dict

from openai import OpenAI
from pydantic import BaseModel

from src.env import SREEnvironment
from src.models import Action, Observation


class ActionEnvelope(BaseModel):
    action: Action


def _observation_to_dict(obs: Observation) -> Dict[str, Any]:
    return obs.model_dump(mode="json")


def choose_action(client: OpenAI, task_name: str, obs: Observation) -> Action:
    system_prompt = (
        "You are an SRE incident response agent. "
        "Return exactly one valid remediation action in the required schema. "
        "Choose only actions that can resolve the root cause with minimal steps."
    )

    user_prompt = (
        f"Task: {task_name}\n"
        "Observation:\n"
        f"{_observation_to_dict(obs)}\n\n"
        "Available actions:\n"
        "- restart_service(service_name: 'web' | 'db' | 'cache')\n"
        "- scale_up(cluster_name: 'web' | 'db' | 'cache', node_count: int > 0)\n"
        "- clear_cache(server_id: str)\n"
        "- page_engineer(team_name: str)\n\n"
        "Output a single action object under the `action` key."
    )

    response = client.responses.parse(
        model="gpt-4o",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        text_format=ActionEnvelope,
    )

    if response.output_parsed is None:
        raise RuntimeError("Model did not return a structured action.")

    return response.output_parsed.action


def run_baseline() -> None:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required to run baseline.py")

    client = OpenAI(api_key=api_key)
    env = SREEnvironment()

    print("Running LLM baseline with gpt-4o...")
    for task_name in ["easy", "medium", "hard"]:
        print(f"\n--- Starting Task: {task_name.upper()} ---")
        obs = env.reset(task_name)
        print(f"Initial Alert: {obs.current_alert} (Severity: {obs.incident_severity})")

        done = False
        reward = None
        info: Dict[str, Any] = {}

        while not done:
            action = choose_action(client, task_name, obs)
            print(f"Agent action: {action.action_type} -> {action.model_dump(mode='json')}")
            obs, reward, done, info = env.step(action)
            print(
                "Step"
                f" {info['step_count']}: score={reward.score}, dense={reward.dense_reward},"
                f" done={done}, msg={reward.message}"
            )

        print(f"Task Complete: {done}")
        print(f"Final Score: {reward.score}")
        print(f"Final Message: {reward.message}")


if __name__ == "__main__":
    run_baseline()
