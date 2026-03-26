import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _filter, _pagination_params
from ..models.inputs import (
    CancelPlaybookRunInput,
    GetPlaybookRunInput,
    ListPlaybookRunsInput,
    ListPlaybooksInput,
    RunPlaybookInput,
)

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
DESTRUCTIVE = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_playbooks(ctx: Context, input: ListPlaybooksInput) -> str:
        """List available playbooks. Filter by active status or name."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.active is not None:
                params.update(_filter("active", str(input.active).lower()))
            if input.name:
                params[f"_filter_name__icontains"] = f'"{input.name}"'
            resp = await client.get("/rest/playbook", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=WRITE)
    async def soar_run_playbook(ctx: Context, input: RunPlaybookInput) -> str:
        """Run a playbook against a container. Provide either playbook_id or playbook_name (repo/name format). Returns a playbook_run_id for polling status."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body: dict = {
                "container_id": input.container_id,
                "run": True,
                "scope": input.scope,
            }
            if input.playbook_id is not None:
                body["playbook_id"] = input.playbook_id
            elif input.playbook_name is not None:
                body["playbook_name"] = input.playbook_name
            else:
                return "Provide either playbook_id or playbook_name."

            resp = await client.post("/rest/playbook_run", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_playbook_run(ctx: Context, input: GetPlaybookRunInput) -> str:
        """Get status of a playbook run. Poll this after soar_run_playbook. Status: running, success, failed."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/playbook_run/{input.playbook_run_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_playbook_runs(ctx: Context, input: ListPlaybookRunsInput) -> str:
        """List playbook runs, optionally filtered by container ID."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.container_id is not None:
                params.update(_filter("container", input.container_id))
            resp = await client.get("/rest/playbook_run", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=DESTRUCTIVE)
    async def soar_cancel_playbook_run(ctx: Context, input: CancelPlaybookRunInput) -> str:
        """Cancel a running playbook. This stops execution — cannot be undone."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.post(
                f"/rest/playbook_run/{input.playbook_run_id}",
                json={"cancel": True},
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
