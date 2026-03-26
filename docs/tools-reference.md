# Splunk SOAR MCP Server - Tools Reference

> **40 tools across 11 domains** for Splunk SOAR On-Prem 6.4.1 / 8.4

---

## Quick Reference

| Domain | Tools | Type |
|--------|-------|------|
| [System](#system) | 4 | Read-only |
| [Containers](#containers) | 5 | Read + Write |
| [Artifacts](#artifacts) | 3 | Read + Write |
| [Playbooks](#playbooks) | 5 | Read + Write + Destructive |
| [Actions](#actions) | 4 | Read + Write + Destructive |
| [Indicators](#indicators) | 5 | Read-only |
| [Notes](#notes) | 3 | Read + Write |
| [Comments](#comments) | 2 | Read + Write |
| [Custom Lists](#custom-lists) | 5 | Read + Write |
| [Approvals](#approvals) | 2 | Read + Write |
| [Assets](#assets) | 2 | Read-only |

**Legend:** All paginated list tools accept `limit` (1-200, default 25) and `page` (0-indexed, default 0).

---

## System

### `soar_get_system_info`
Get SOAR system info: version, hostname, product, license details. Use to verify connectivity.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| *(none)* | | | |

### `soar_list_apps`
List installed SOAR apps with their supported action types.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |

### `soar_get_container_options`
Get valid values for container status, severity, label, and sensitivity fields.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| *(none)* | | | |

### `soar_get_app_actions`
Get actions supported by a specific SOAR app. Use `soar_list_apps` first to find the app ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `app_id` | int | **Yes** | App ID to retrieve actions for |

---

## Containers

### `soar_list_containers`
List SOAR containers (events/cases). Filter by status, label, severity. Returns paginated results.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `status` | string | No | Filter by status (`new`, `open`, `closed`, `resolved`) |
| `label` | string | No | Filter by label (e.g. `events`) |
| `severity` | string | No | Filter by severity (`high`, `medium`, `low`) |
| `sort` | string | No | Sort field (e.g. `id`, `-create_time`) |

### `soar_get_container`
Get full details for a single container including custom_fields and workbook info.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container_id` | int | **Yes** | Container ID |

### `soar_create_container`
Create a new SOAR container (event or case). If `source_data_identifier` matches an existing container, returns the existing ID with `failed=true` instead of creating a duplicate.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | **Yes** | | Container name |
| `label` | string | No | `events` | Container label |
| `severity` | string | No | `medium` | `high`, `medium`, `low` |
| `sensitivity` | string | No | | TLP: `red`, `amber`, `green`, `white` |
| `status` | string | No | `new` | `new`, `open`, `closed`, `resolved` |
| `container_type` | string | No | `default` | `default` (event) or `case` |
| `source_data_identifier` | string | No | | SDI dedup key |
| `owner_id` | string | No | | Owner username or email |
| `tags` | list[string] | No | | Tags to apply |
| `run_automation` | bool | No | `false` | Trigger active playbooks on creation |

### `soar_update_container`
Update a container's status, severity, sensitivity, owner, or tags.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container_id` | int | **Yes** | Container ID to update |
| `status` | string | No | New status |
| `severity` | string | No | New severity |
| `sensitivity` | string | No | New sensitivity |
| `owner_id` | string | No | New owner |
| `tags` | list[string] | No | Replace tags |

### `soar_get_container_audit`
Get audit trail for a container. **WARNING:** reading audit logs creates an audit event itself -- use sparingly.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container_id` | int | **Yes** | Container ID |
| `sort` | string | No | Sort field |

---

## Artifacts

### `soar_list_artifacts`
List artifacts, optionally filtered by container ID. Returns paginated results with CEF fields.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `container_id` | int | No | Filter by container ID |

### `soar_create_artifact`
Create an artifact on a container with CEF fields. For batch creation, set `run_automation=false` on all but the last artifact to avoid triggering playbooks N times.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `container_id` | int | **Yes** | | Container to attach artifact to |
| `name` | string | No | `artifact` | Artifact name |
| `label` | string | No | `event` | Artifact label |
| `cef` | dict | **Yes** | | CEF fields (e.g. `{"sourceAddress": "1.2.3.4"}`) |
| `cef_types` | dict | No | | CEF type overrides (e.g. `{"sourceAddress": ["ip"]}`) |
| `tags` | list[string] | No | | Tags |
| `run_automation` | bool | No | `true` | Trigger playbooks (set `false` for batch except last) |

### `soar_get_artifact`
Get full details for a single artifact including CEF fields and metadata.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `artifact_id` | int | **Yes** | Artifact ID |

---

## Playbooks

### `soar_list_playbooks`
List available playbooks. Filter by active status or name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `active` | bool | No | Filter by active status |
| `name` | string | No | Filter by playbook name (contains) |

### `soar_run_playbook`
Run a playbook against a container. Provide either `playbook_id` or `playbook_name` (repo/name format). Returns a `playbook_run_id` for polling status.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `container_id` | int | **Yes** | | Container ID to run playbook against |
| `playbook_id` | int | No | | Playbook ID (use this OR `playbook_name`) |
| `playbook_name` | string | No | | Playbook name as `repo/name` (use this OR `playbook_id`) |
| `scope` | string | No | `all` | Artifact scope: `all` or `new` |

### `soar_get_playbook_run`
Get status of a playbook run. Poll this after `soar_run_playbook`. Status: `running`, `success`, `failed`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playbook_run_id` | int | **Yes** | Playbook run ID |

### `soar_list_playbook_runs`
List playbook runs, optionally filtered by container ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `container_id` | int | No | Filter by container ID |

### `soar_cancel_playbook_run`
Cancel a running playbook. This stops execution -- **cannot be undone**.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playbook_run_id` | int | **Yes** | Playbook run ID to cancel |

---

## Actions

### `soar_run_action`
Run an app action (e.g. `geolocate ip`) against a container. Returns `action_run_id` for polling. Use `soar_list_assets` to find valid asset names for targets.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action` | string | **Yes** | | Action name (e.g. `geolocate ip`) |
| `container_id` | int | **Yes** | | Container ID |
| `action_type` | string | No | `investigate` | `investigate`, `contain`, `correct`, `generic` |
| `targets` | list[dict] | **Yes** | | `[{assets: [name], parameters: [{key: value}]}]` |

### `soar_get_action_run`
Get status and results of an action run. Poll after `soar_run_action`. Result data is in `result_data[0].data`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_run_id` | int | **Yes** | Action run ID |

### `soar_list_action_runs`
List action runs, optionally filtered by container ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `container_id` | int | No | Filter by container ID |

### `soar_cancel_action_run`
Cancel a running action. This stops execution -- **cannot be undone**.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_run_id` | int | **Yes** | Action run ID to cancel |

---

## Indicators

### `soar_list_indicators`
List threat indicators aggregated across containers. Shows open/total events, severity counts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `timerange` | string | No | `last_30_days`, `last_7_days`, etc. |
| `sort` | string | No | Sort field |

### `soar_get_indicator`
Get details for a single indicator including open_events, severity counts, and time range.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `indicator_id` | int | **Yes** | Indicator ID |

### `soar_get_indicator_by_value`
Look up an indicator by its value (IP, hash, domain, etc.).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `indicator_value` | string | **Yes** | Indicator value (e.g. IP, hash, domain) |

### `soar_get_indicator_artifacts`
Get all artifacts that share a given indicator. Useful for cross-container correlation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `indicator_id` | int | **Yes** | Indicator ID |

### `soar_get_top_indicators`
Get the most frequently seen indicators (IOCs) across all containers.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |

---

## Notes

### `soar_add_note`
Add a structured note to a container. Notes support markdown and can be attached to workbook phases. Use for analyst findings; use comments for quick annotations.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `container_id` | int | **Yes** | | Container ID |
| `title` | string | **Yes** | | Note title |
| `content` | string | **Yes** | | Note content (supports markdown) |
| `note_type` | string | No | `general` | `general` or `fact` |
| `phase_id` | int | No | | Workbook phase ID |

### `soar_list_notes`
List notes, optionally filtered by container ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `container_id` | int | No | Filter by container ID |

### `soar_get_note`
Get a single note with full content and attachments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `note_id` | int | **Yes** | Note ID |

---

## Comments

### `soar_add_comment`
Add a simple text comment to a container. For structured findings, use `soar_add_note` instead.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container_id` | int | **Yes** | Container ID |
| `comment` | string | **Yes** | Comment text |

### `soar_list_comments`
List comments on containers, optionally filtered by container ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `container_id` | int | No | Filter by container ID |

---

## Custom Lists

### `soar_list_all_lists`
List all custom lists (decided_lists) with names and IDs.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |

### `soar_get_list`
Get a custom list's content (2D array) by name or ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name_or_id` | string | **Yes** | List name or numeric ID |

### `soar_get_list_formatted`
Get a custom list as delimited text (useful for display).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | **Yes** | List name |

### `soar_update_list`
Update a custom list: append rows, delete rows by index, or update specific rows. Cannot delete all rows -- at least one must remain.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name_or_id` | string | **Yes** | List name or numeric ID |
| `append_rows` | list[list[string]] | No | Rows to append |
| `delete_rows` | list[int] | No | Row indices to delete |
| `update_rows` | dict[string, list[string]] | No | Row index -> new values |

### `soar_create_list`
Create a new custom list with a name and initial content (2D array of rows).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | **Yes** | List name |
| `content` | list[list[string]] | **Yes** | 2D array of rows |

---

## Approvals

### `soar_list_approvals`
List approval tasks (workbook tasks). Defaults to pending approvals.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | int | No | 25 | Page size (1-200) |
| `page` | int | No | 0 | Page number (0-indexed) |
| `status` | string | No | `pending` | Filter by status |

### `soar_respond_to_approval`
Respond to a pending approval task (approve, decline, etc.).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | int | **Yes** | Workbook task ID |
| `response_value` | string | **Yes** | Response value (e.g. `approve`, `decline`) |

---

## Assets

### `soar_list_assets`
List configured assets. Asset names are needed for `soar_run_action` targets. Filter by product name or vendor.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | int | No | Page size (1-200, default 25) |
| `page` | int | No | Page number (0-indexed) |
| `product_name` | string | No | Filter by product name |
| `product_vendor` | string | No | Filter by product vendor |

### `soar_get_asset`
Get full details for an asset including configuration and action_whitelist.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `asset_id` | int | **Yes** | Asset ID |

---

## Common Workflows

### Investigate an IP
```
1. soar_create_container      -- create event for the investigation
2. soar_create_artifact       -- add IP as artifact with cef: {sourceAddress: "1.2.3.4"}
3. soar_list_assets           -- find asset name for your enrichment app
4. soar_run_action            -- run "geolocate ip" or "ip reputation"
5. soar_get_action_run        -- poll until status is "success"
6. soar_add_note              -- document findings
```

### Triage containers
```
1. soar_list_containers       -- filter by status="new", severity="high"
2. soar_get_container         -- get full details
3. soar_list_artifacts        -- review artifacts (IOCs)
4. soar_get_indicator_by_value -- cross-reference indicator across all events
5. soar_update_container      -- set status="open", assign owner
```

### Batch artifact ingestion
```
1. soar_create_artifact(run_automation=false)  -- artifact 1
2. soar_create_artifact(run_automation=false)  -- artifact 2
3. soar_create_artifact(run_automation=true)   -- last artifact triggers playbooks
```
