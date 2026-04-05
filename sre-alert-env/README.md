# Cloud Infrastructure Alert Manager (Minimal SRE)

A minimal, deterministic SRE simulation environment for OpenEnv. The agent must respond to infrastructure alerts across three services by taking appropriate mitigation actions.

## State Fields (Observation)
The environment provides the following state per service/cluster:
- **Services**: `web`, `db`, `cache`
- **Metrics**: 
  - `cpu` (0.0 to 1.0)
  - `memory` (0.0 to 1.0)
  - `disk` (0.0 to 1.0)
  - `latency` (ms)
  - `error_count` (int)
- **Status Indicators**: `current_alert` (string), `incident_severity` (low/medium/high), `resolved` (boolean)

## Actions
The agent can perform one of four remediation actions:
- `restart_service(service_name: str)`
- `scale_up(cluster_name: str, node_count: int)`
- `clear_cache(server_id: str)`
- `page_engineer(team_name: str)`

## Scenarios (Tasks)
1. **Easy: Disk alert on DB server.**
   - Context: `db` service is showing high disk usage.
   - Ideal resolution: `clear_cache("db-server-1")` or `restart_service("db")`.
2. **Medium: Web latency spike.**
   - Context: Traffic spike causes high API latency on the `web` cluster.
   - Ideal resolution: `scale_up("web", 3)`. (Do not touch DB).
3. **Hard: DB failure with noisy frontend errors.**
   - Context: Database has failed, causing a flood of noisy errors in the frontend (`web`).
   - Ideal resolution: Identify DB as root cause -> `restart_service("db")` and `page_engineer("db-team")`.

## Rewards
- Positive reward for improving metrics or resolving root cause.
- Negative reward for targeting the wrong service, unnecessary scaling, paging the wrong team, or taking inefficient/extra steps.
