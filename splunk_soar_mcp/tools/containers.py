import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _filter, _pagination_params
from ..models.inputs import (
    CreateContainerInput,
    GetContainerAuditInput,
    GetContainerInput,
    ListContainersInput,
    UpdateContainerInput,
)

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
WRITE_IDEMPOTENT = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_containers(ctx: Context, input: ListContainersInput) -> str:
        """List SOAR containers (events/cases). Filter by status, label, severity. Returns paginated results."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.status:
                params.update(_filter("status", input.status))
            if input.label:
                params.update(_filter("label", input.label))
            if input.severity:
                params.update(_filter("severity", input.severity))
            if input.sort:
                params["sort"] = input.sort
            resp = await client.get("/rest/container", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_container(ctx: Context, input: GetContainerInput) -> str:
        """Get full details for a single container including custom_fields and workbook info."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/container/{input.container_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=WRITE)
    async def soar_create_container(ctx: Context, input: CreateContainerInput) -> str:
        """Create a new SOAR container (event or case). If source_data_identifier matches an existing container, returns the existing ID with failed=true instead of creating a duplicate."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body: dict = {
                "name": input.name,
                "label": input.label,
                "severity": input.severity,
                "status": input.status,
                "container_type": input.container_type,
                "run_automation": input.run_automation,
            }
            if input.sensitivity:
                body["sensitivity"] = input.sensitivity
            if input.source_data_identifier:
                body["source_data_identifier"] = input.source_data_identifier
            if input.owner_id:
                body["owner_id"] = input.owner_id
            if input.tags:
                body["tags"] = input.tags

            resp = await client.post("/rest/container", json=body)
            resp.raise_for_status()
            data = resp.json()

            if data.get("failed"):
                existing_id = data.get("existing_container_id", "unknown")
                return json.dumps({
                    "status": "duplicate",
                    "message": f"Container with this SDI already exists (ID: {existing_id})",
                    "existing_container_id": existing_id,
                    "response": data,
                }, indent=2)

            return json.dumps(data, indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=WRITE_IDEMPOTENT)
    async def soar_update_container(ctx: Context, input: UpdateContainerInput) -> str:
        """Update a container's status, severity, sensitivity, owner, or tags."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body: dict = {}
            if input.status is not None:
                body["status"] = input.status
            if input.severity is not None:
                body["severity"] = input.severity
            if input.sensitivity is not None:
                body["sensitivity"] = input.sensitivity
            if input.owner_id is not None:
                body["owner_id"] = input.owner_id
            if input.tags is not None:
                body["tags"] = input.tags

            if not body:
                return "No fields to update. Provide at least one field."

            resp = await client.post(f"/rest/container/{input.container_id}", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_container_audit(ctx: Context, input: GetContainerAuditInput) -> str:
        """Get audit trail for a container. WARNING: reading audit logs creates an audit event itself — use sparingly."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params: dict = {}
            if input.sort:
                params["sort"] = input.sort
            resp = await client.get(f"/rest/container/{input.container_id}/audit", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
