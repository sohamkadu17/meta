import os
import json
import re
from typing import Any, Dict

from openai import OpenAI
from pydantic import BaseModel

from src.env import SREEnvironment
from src.models import Action, Observation


class ActionEnvelope(BaseModel):
    action: Action


VALID_ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "action_type": {"const": "restart_service"},
                        "service_name": {"enum": ["web", "db", "cache"]},
                    },
                    "required": ["action_type", "service_name"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "action_type": {"const": "scale_up"},
                        "cluster_name": {"enum": ["web", "db", "cache"]},
                        "node_count": {"type": "integer", "minimum": 1},
                    },
                    "required": ["action_type", "cluster_name", "node_count"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "action_type": {"const": "clear_cache"},
                        "server_id": {"type": "string"},
                    },
                    "required": ["action_type", "server_id"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "action_type": {"const": "page_engineer"},
                        "team_name": {"type": "string"},
                    },
                    "required": ["action_type", "team_name"],
                    "additionalProperties": False,
                },
            ]
        }
    },
    "required": ["action"],
    "additionalProperties": False,
}


def _observation_to_dict(obs: Observation) -> Dict[str, Any]:
    return obs.model_dump(mode="json")


def _extract_json(content: str) -> Dict[str, Any]:
    content = content.strip()

    # Handle fenced JSON output
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))

    # Handle raw JSON output
    if content.startswith("{") and content.endswith("}"):
        return json.loads(content)

    # Last-resort object extraction if model wrapped extra text around JSON
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(content[start : end + 1])

    raise RuntimeError("Model response did not contain valid JSON.")


def build_client() -> OpenAI:
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()

    # Local OpenAI-compatible servers often do not require a key.
    if not api_key:
        api_key = "local"

    kwargs: Dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def choose_action(client: OpenAI, model: str, task_name: str, obs: Observation) -> Action:
    system_prompt = (
        "You are an SRE incident response agent. "
        "Choose the next best action for the current incident. "
        "Return JSON only, with no extra text."
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
        "Output strictly one JSON object under the `action` key using this schema:\n"
        f"{json.dumps(VALID_ACTION_SCHEMA)}"
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Model returned empty content.")

    payload = _extract_json(content)
    envelope = ActionEnvelope.model_validate(payload)
    return envelope.action


def run_baseline() -> None:
    model = os.getenv("LLM_MODEL", "gpt-4o")
    client = build_client()
    env = SREEnvironment()

    print("Running LLM baseline...")
    print(f"Model: {model}")
    print(f"Base URL: {os.getenv('LLM_BASE_URL', 'default OpenAI endpoint')}")

    for task_name in ["easy", "medium", "hard"]:
        print(f"\n--- Starting Task: {task_name.upper()} ---")
        obs = env.reset(task_name)
        print(f"Initial Alert: {obs.current_alert} (Severity: {obs.incident_severity})")

        done = False
        reward = None
        info: Dict[str, Any] = {}

        while not done:
            action = choose_action(client, model, task_name, obs)
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
