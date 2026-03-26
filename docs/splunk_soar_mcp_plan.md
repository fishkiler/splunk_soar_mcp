# splunk_soar_mcp — Build Plan

> **Target:** Splunk SOAR On-Premises 6.4.1 / 8.4  
> **Transport:** stdio (primary — for Claude Code / Windsurf) + optional HTTP  
> **Language:** Python + FastMCP  
> **Auth:** `ph-auth-token` header (automation user)

---

## Project Structure

```
splunk_soar_mcp/
├── server.py              # FastMCP entry point + lifespan (HTTP client)
├── config.py              # Env vars: SOAR_HOST, SOAR_TOKEN, SOAR_VERIFY_SSL
├── client.py              # Shared httpx client factory + _err() + _fmt() helpers
├── tools/
│   ├── __init__.py
│   ├── containers.py      # soar_list_containers, soar_get_container, create, update, audit
│   ├── artifacts.py       # soar_list_artifacts, soar_create_artifact
│   ├── playbooks.py       # soar_list_playbooks, soar_run_playbook, soar_get_playbook_run
│   ├── actions.py         # soar_run_action, soar_get_action_run, soar_list_action_runs
│   ├── assets.py          # soar_list_assets, soar_get_asset
│   ├── indicators.py      # soar_list_indicators, soar_get_indicator, soar_indicator_by_value
│   ├── notes.py           # soar_add_note, soar_list_notes
│   ├── lists.py           # soar_get_list, soar_update_list, soar_list_all_lists
│   ├── approvals.py       # soar_list_approvals, soar_respond_to_approval
│   ├── comments.py        # soar_add_comment, soar_list_comments
│   └── system.py          # soar_get_system_info, soar_list_apps, soar_get_container_options
├── models/
│   ├── __init__.py
│   └── inputs.py          # All Pydantic input models
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Authentication & Configuration

```python
# config.py
SOAR_HOST      = os.getenv("SOAR_HOST", "https://localhost")
SOAR_TOKEN     = os.getenv("SOAR_TOKEN", "")          # ph-auth-token value
SOAR_USER      = os.getenv("SOAR_USER", "")           # optional: basic auth username
SOAR_PASS      = os.getenv("SOAR_PASS", "")           # optional: basic auth password
SOAR_VERIFY_SSL = os.getenv("SOAR_VERIFY_SSL", "false").lower() not in ("false", "0", "no")
```

**Token auth** (recommended) — automation user, `ph-auth-token` in headers.  
**Basic auth** fallback — some ops (delete, certain admin) require user auth. If `SOAR_USER`/`SOAR_PASS` are set, use `httpx.BasicAuth` instead of token header.

**Getting the token:**
1. SOAR admin → Administration → User Management → Users → + User
2. Type = **Automation**, role = **Automation** (or custom scoped role)
3. Allowed IPs = IP of your dev machine (or `any`)
4. Click user name → copy `ph-auth-token` from the JSON config panel

---

## Shared Infrastructure (client.py)

```python
# Shared lifespan-managed client
@asynccontextmanager
async def app_lifespan():
    async with httpx.AsyncClient(
        base_url=SOAR_HOST,
        headers={"ph-auth-token": SOAR_TOKEN},
        verify=SOAR_VERIFY_SSL,
        timeout=30.0,
    ) as client:
        yield {"client": client}

# Error handler
def _err(e: Exception) -> str:
    # 401 → token check message
    # 403 → permission message  
    # 404 → not found + verify ID
    # 429 → rate limit
    # ConnectError → check SOAR_HOST
    # TimeoutException → SOAR busy

# Pagination helper
def _pagination_params(limit: int, page: int) -> dict:
    return {"page_size": limit, "page": page}

# SOAR filter query helper  
# SOAR uses ?_filter_field="value" syntax for server-side filtering
def _filter(field: str, value: str) -> dict:
    return {f"_filter_{field}": f'"{value}"'}
```

---

## Tool Inventory (33 tools across 12 domains)

### 1. Containers — `tools/containers.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_containers` | GET | `/rest/container` | Filters: status, label, severity, sort, page |
| `soar_get_container` | GET | `/rest/container/<id>` | Full detail including custom_fields, workbook |
| `soar_create_container` | POST | `/rest/container` | type: default (event) or case |
| `soar_update_container` | POST | `/rest/container/<id>` | status, severity, owner, tags, sensitivity |
| `soar_get_container_options` | GET | `/rest/container_options` | Returns valid status/severity/label/sensitivity values |
| `soar_get_container_audit` | GET | `/rest/container/<id>/audit` | Full change history; params: sort, start, end, format |

**Key fields for create:**
```json
{
  "name": "string",
  "label": "events",
  "severity": "high|medium|low",
  "sensitivity": "red|amber|green|white",
  "status": "new|open|closed|resolved",
  "container_type": "default|case",
  "source_data_identifier": "string (dedup key)",
  "owner_id": "username or email",
  "tags": ["tag1"],
  "run_automation": false
}
```

**Duplicate handling:** If SDI + asset_id match existing container, API returns `{"existing_container_id": N, "failed": true}`. The tool should surface this clearly.

---

### 2. Artifacts — `tools/artifacts.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_artifacts` | GET | `/rest/artifact` | Filter by `_filter_container_id` |
| `soar_create_artifact` | POST | `/rest/artifact` | CEF fields, cef_types, run_automation |
| `soar_get_artifact` | GET | `/rest/artifact/<id>` | Single artifact detail |

**Important:** For batch artifact creation, set `run_automation=false` on all but the last artifact to avoid triggering playbooks N times.

**CEF type overrides** (`cef_types`): Tell SOAR what a field *contains*, e.g. `{"sourceAddress": ["ip"], "fileHash": ["hash"]}`. Enables playbook data path resolution.

**Artifact create body:**
```json
{
  "container_id": 12,
  "name": "artifact",
  "label": "event",
  "cef": {
    "sourceAddress": "1.2.3.4",
    "destinationPort": 443,
    "fileHash": "abc123..."
  },
  "cef_types": {"sourceAddress": ["ip"], "fileHash": ["hash"]},
  "tags": [],
  "run_automation": true
}
```

---

### 3. Playbooks — `tools/playbooks.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_playbooks` | GET | `/rest/playbook` | Filters: active, repo, name |
| `soar_run_playbook` | POST | `/rest/playbook_run` | Returns playbook_run_id |
| `soar_get_playbook_run` | GET | `/rest/playbook_run/<id>` | Poll status: running/success/failed |
| `soar_list_playbook_runs` | GET | `/rest/playbook_run` | Filter by `_filter_container` |
| `soar_cancel_playbook_run` | POST | `/rest/playbook_run/<id>` | Body: `{"cancel": true}` |

**Run playbook body:**
```json
{
  "container_id": 12,
  "playbook_id": 42,        // OR use playbook_name
  "playbook_name": "local/my_playbook",
  "run": true,
  "scope": "all"            // "all" or "new" artifacts
}
```

**Playbook toggle (activate/deactivate):**
- POST to `/rest/playbook/<id>` with `{"active": true/false, "cancel_runs": true}`
- Useful for enabling/disabling playbooks programmatically

**Export/Import:**
- Export: GET `/rest/playbook/<id>/export` → gzipped TGZ
- Import: POST `/rest/import_playbook` with base64-encoded TGZ

---

### 4. Actions (App Runs) — `tools/actions.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_run_action` | POST | `/rest/action_run` | Returns action_run_id immediately |
| `soar_get_action_run` | GET | `/rest/action_run/<id>` | Poll: running/success/failed |
| `soar_list_action_runs` | GET | `/rest/action_run` | Filter by `_filter_container` |
| `soar_cancel_action_run` | POST | `/rest/action_run/<id>/cancel` | Cancel running action |

**Action run body:**
```json
{
  "action": "geolocate ip",
  "container_id": 12,
  "type": "investigate",    // investigate|contain|correct|generic
  "targets": [{
    "app_id": 23,           // optional, auto-resolved from asset
    "assets": ["maxmind"],  // asset name(s)
    "parameters": [{"ip": "1.2.3.4"}]
  }]
}
```

**Result data lives at:** `result_data[0]["data"]` after polling `soar_get_action_run`

**Action types:** `investigate` (read-only enrichment), `contain` (blocking), `correct` (remediation), `generic`

---

### 5. Assets — `tools/assets.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_assets` | GET | `/rest/asset` | Filters: product_name, product_vendor |
| `soar_get_asset` | GET | `/rest/asset/<id>` | Full config including action_whitelist |

Asset name (not ID) is what you pass to `soar_run_action`. Always `soar_list_assets` first to find valid names.

---

### 6. Indicators — `tools/indicators.py`  
*(Added from 6.4.1 docs — significant feature missing from initial build)*

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_indicators` | GET | `/rest/indicator` | Filters: timerange, sort, page; `_special_fields=true` |
| `soar_get_indicator` | GET | `/rest/indicator/<id>` | Returns open_events, total_events, severity_counts |
| `soar_get_indicator_by_value` | GET | `/rest/indicator_by_value` | Param: `indicator_value=<value>` |
| `soar_get_indicator_artifacts` | GET | `/rest/indicator_artifact` | Param: `indicator_id=<id>` — all artifacts sharing this IOC |
| `soar_get_top_indicators` | GET | `/rest/top_indicator` | Returns most frequently seen IOCs |

**Indicator response fields:**
```json
{
  "id": 6,
  "value": "1.2.3.4",
  "_special_fields": ["sourceAddress"],
  "_special_contains": ["ip"],
  "_special_labels": ["events"],
  "open_events": 347,
  "total_events": 509,
  "sc_high": 299, "sc_medium": 110, "sc_low": 100,
  "earliest_time": "...", "latest_time": "..."
}
```

**Query params for list:** `_special_fields=true`, `_special_labels=true`, `_special_contains=true`, `_special_severity=true`, `timerange=last_30_days|last_7_days|etc`

---

### 7. Notes — `tools/notes.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_add_note` | POST | `/rest/note` | title, content, note_type (general\|fact), phase_id |
| `soar_list_notes` | GET | `/rest/note` | Filter by `_filter_container_id` |
| `soar_get_note` | GET | `/rest/note/<id>` | Single note with attachments |

**Note body:**
```json
{
  "container_id": 12,
  "title": "Analysis Summary",
  "content": "## Findings\n...",
  "note_type": "general",   // "general" or "fact"
  "phase_id": 3             // optional: workbook phase
}
```

---

### 8. Custom Lists — `tools/lists.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_all_lists` | GET | `/rest/decided_list` | Returns all list names and IDs |
| `soar_get_list` | GET | `/rest/decided_list/<name_or_id>` | Returns content (2D array) |
| `soar_get_list_formatted` | GET | `/rest/decided_list/<name>/formatted_content` | Returns delimited text |
| `soar_update_list` | POST | `/rest/decided_list/<name_or_id>` | append_rows, delete_rows, update_rows |
| `soar_create_list` | POST | `/rest/decided_list` | name + content (2D array) |

**Update body (partial):**
```json
{
  "append_rows": [["1.2.3.4", "C2 server", "high"]],
  "delete_rows": [0, 5],
  "update_rows": {"2": ["8.8.8.8", "DNS", "low"]}
}
```
**Constraint:** Cannot delete all rows — at least one must remain.  
**Limit:** 256 MB per list. Lists are stored as a single string in DB.

---

### 9. Approvals — `tools/approvals.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_approvals` | GET | `/rest/workbook_task` | Filter: `_filter_status="pending"` |
| `soar_respond_to_approval` | POST | `/rest/workbook_task/<id>` | Body: `{"responses": [{"value": "approve"}]}` |

**Note:** Approvals in SOAR are a type of workbook task. The correct endpoint is `/rest/workbook_task`, not `/rest/approval` (which is a legacy endpoint).

---

### 10. Comments — `tools/comments.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_add_comment` | POST | `/rest/container_comment` | container_id + comment string |
| `soar_list_comments` | GET | `/rest/container_comment` | Filter by `_filter_container_id` |

**Distinct from Notes:** Comments are simple inline text attached to a container. Notes are structured with title/type/phase and support markdown + attachments. For analyst findings use Notes; for quick annotations use Comments.

---

### 11. System & Admin — `tools/system.py`

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_get_system_info` | GET | `/rest/system_info` | Version, hostname, product name |
| `soar_list_apps` | GET | `/rest/app` | Installed apps + supported action types |
| `soar_get_container_options` | GET | `/rest/container_options` | Valid status/severity/label/sensitivity enums |
| `soar_get_app_actions` | GET | `/rest/app/<id>` | Actions supported by a specific app |

**`/rest/system_info` response includes:**
- `version`, `hostname`, `product_name`, `product_vendor`
- `license` details
- `installation_id`

---

### 12. Evidence (Vault) — Optional/Future

| Tool | Method | Endpoint | Notes |
|------|--------|----------|-------|
| `soar_list_evidence` | GET | `/rest/evidence` | Filter by container, content_type_model |
| `soar_add_attachment` | POST | `/rest/container_attachment` | base64 file_content + file_name + container_id |

**Attachment body:**
```json
{
  "container_id": 12,
  "file_name": "malware_sample.exe",
  "file_content": "<base64 encoded bytes>",
  "task_id": 80,
  "metadata": {"contains": ["vault id", "hash"]}
}
```
Returns `vault_id` (SHA1 hash). Deprioritize for initial build — adds complexity.

---

## Key API Behaviors & Gotchas

### Filtering Syntax
SOAR uses a custom filter query param format:
```
# Exact match
?_filter_status="new"

# Contains (case-insensitive)
?_filter_product_name__icontains="splunk"

# Integer match  
?_filter_container_id=12

# Multiple values (use field separator %1E)
?_filter_status="new"%1E"open"
```

### Pagination
All list endpoints use:
```
?page=0&page_size=25
```
Response always includes `count`, `num_pages`, `data`.

### run_automation Flag
- When creating artifacts in bulk: set `run_automation=false` on all but the **last** one
- This prevents playbooks firing N times
- If creating container+artifacts in a single POST, SOAR handles this automatically

### source_data_identifier (SDI)
- Acts as a dedup key per asset
- Duplicate SDI + asset_id combo returns `{"existing_container_id": N, "failed": true}` — **not a 4xx error**, it's a 200
- Tools should check for `failed: true` in the response and surface it clearly

### Action Run Results Shape
```json
{
  "id": 47,
  "status": "success",
  "result_summary": {"total_objects": 1, "total_objects_successful": 1},
  "result_data": [{
    "status": "success",
    "message": "Country: India",
    "data": [{"country_name": "India", ...}],
    "parameter": {"ip": "103.230.84.239"},
    "summary": {"country": "India"}
  }]
}
```

### Audit Logging
- **Reading container/playbook audit logs IS itself logged as an audit event**
- Every GET to `/rest/container/<id>/audit` generates a new audit record
- Use sparingly — not in tight polling loops

### Token vs Basic Auth
- **Token** (`ph-auth-token`): Works for all read + write operations
- **Basic auth**: Required for DELETE operations
- Plan: Support both; default to token, fall back to basic if `SOAR_USER`/`SOAR_PASS` are set

---

## Pydantic Model Patterns

```python
# Shared base for paginated list inputs
class ListInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    limit: int = Field(default=25, ge=1, le=200)
    page: int = Field(default=0, ge=0)

# All models: ConfigDict(str_strip_whitespace=True, extra="forbid")
# All fields: explicit Field(...) with description
# Enums via Literal types for constrained choices
```

---

## Tool Annotations Cheatsheet

```python
# Read-only lookup
{"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}

# Write (create)
{"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}

# Write (update / idempotent)  
{"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}

# Cancel / block (potentially destructive)
{"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}
```

---

## Environment Variables

```bash
# Required
SOAR_HOST=https://192.168.1.x       # Your SOAR instance URL
SOAR_TOKEN=your-ph-auth-token       # From SOAR automation user

# Optional
SOAR_VERIFY_SSL=false               # false for self-signed certs (dev)
SOAR_USER=soar_local_admin          # For basic auth / delete ops
SOAR_PASS=changeme
MCP_PORT=8000                       # HTTP transport port (default 8000)
```

`.env.example`:
```
SOAR_HOST=https://localhost
SOAR_TOKEN=
SOAR_VERIFY_SSL=false
SOAR_USER=soar_local_admin
SOAR_PASS=
```

---

## Claude Code / Windsurf MCP Config

```json
{
  "mcpServers": {
    "splunk_soar": {
      "command": "python",
      "args": ["${workspaceFolder}/server.py"],
      "env": {
        "SOAR_HOST": "https://your-dev-soar",
        "SOAR_TOKEN": "your-token",
        "SOAR_VERIFY_SSL": "false"
      }
    }
  }
}
```

Or with `uv`:
```json
{
  "mcpServers": {
    "splunk_soar": {
      "command": "uv",
      "args": ["run", "--directory", "${workspaceFolder}", "server.py"]
    }
  }
}
```

---

## Dependencies (pyproject.toml)

```toml
[project]
name = "splunk-soar-mcp"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "httpx"]
```

---

## Build Order Recommendation

1. `config.py` + `client.py` — auth, lifespan, helpers
2. `models/inputs.py` — all Pydantic models upfront
3. `tools/system.py` — test auth + connection early with `soar_get_system_info`
4. `tools/containers.py` — core workflow object
5. `tools/artifacts.py` — goes with containers
6. `tools/playbooks.py` + `tools/actions.py` — execution layer
7. `tools/indicators.py` — threat intel layer
8. `tools/notes.py` + `tools/comments.py` — annotation layer
9. `tools/lists.py` + `tools/approvals.py` — supporting workflows
10. `tools/assets.py` + `server.py` wiring

---

## Testing Against Dev Instance

```bash
# Verify auth works
curl -k -H "ph-auth-token: YOUR_TOKEN" https://YOUR_SOAR/rest/system_info

# Quick test via MCP inspector
npx @modelcontextprotocol/inspector uv run server.py

# Syntax check only
python -m py_compile server.py
```
