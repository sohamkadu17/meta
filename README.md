# 🌩️ Cloud Infrastructure Alert Manager
**OpenEnv Spec Compliant DevOps/SRE Training Environment**

![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-0A84FF)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB)
![Pydantic](https://img.shields.io/badge/Pydantic-Strict_Typed_Models-E92063)
![FastAPI](https://img.shields.io/badge/FastAPI-HF_Ready-009688)
![Docker](https://img.shields.io/badge/Docker-Hugging_Face_Spaces-2496ED)

## 📖 Environment Description and Motivation
Modern production systems fail in ways that are noisy, multi-causal, and time-sensitive. A single infrastructure incident can quickly cascade across services, creating false signals and overwhelming responders. 

This project simulates that operational reality for AI agents in a deterministic, OpenEnv-compatible environment. The agent receives structured production alerts and service metrics, then selects remediation actions such as scaling compute, restarting dependencies, clearing cache, or paging the correct engineering team.

**Why This Matters:**
* **Faster recovery:** Automated first-response can reduce incident resolution time.
* **Lower pager load:** Agents can handle obvious mitigations before escalating.
* **Better reliability:** Structured, graded behavior encourages root-cause-oriented remediation rather than shallow symptom fixes.
* **Safer experimentation:** Models can be trained and evaluated on deterministic incidents without production risk.

## ✅ OpenEnv Specification Compliance
This environment is designed to strictly align with OpenEnv hackathon requirements:
- [x] **State machine methods implemented:** `reset`, `step`, `state`
- [x] **Strict typed spaces using Pydantic:** Observation model, Action union model, Reward model
- [x] **Three deterministic tasks:** Easy, Medium, Hard
- [x] **Deterministic grading logic:** Score range from `0.0` to `1.0`
- [x] **Meaningful Reward Function:** Dense reward signals for progress and penalties for inefficient or harmful actions
- [x] **Baseline runner:** Provider-agnostic inference script using LLM APIs
- [x] **Deployment:** Dockerized deployment with web service on port `7860` for Hugging Face Spaces

---

## 👁️ Observation Space
The AI agent receives a typed `Observation` object with full service telemetry and incident context.

**Service Topology:** `web`, `db`, `cache`

**Per-Service Metrics:**
* `cpu_usage`: float in [0.0, 1.0]
* `memory_usage`: float in [0.0, 1.0]
* `disk_usage`: float in [0.0, 1.0]
* `latency_ms`: float >= 0.0
* `error_count`: int >= 0

**Incident Context:**
* `current_alert`: optional string
* `incident_severity`: low, medium, high, critical
* `resolved`: boolean

```json
{
  "services": {
    "web": {"cpu_usage": 0.95, "latency_ms": 1200.0, "status": "degraded"},
    "db": {"cpu_usage": 0.40, "latency_ms": 15.0, "status": "healthy"}
  },
  "current_alert": "HIGH_LATENCY_WEB",
  "incident_severity": "high",
  "resolved": false
}