import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _filter, _pagination_params
from ..models.inputs import (
    CancelActionRunInput,
    GetActionRunInput,
    ListActionRunsInput,
    RunActionInput,
)

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
DESTRUCTIVE = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=WRITE)
    async def soar_run_action(ctx: Context, input: RunActionInput) -> str:
        """Run an app action (e.g. 'geolocate ip') against a container. Returns action_run_id for polling. Use soar_list_assets to find valid asset names for targets."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body = {
                "action": input.action,
                "container_id": input.container_id,
                "type": input.action_type,
                "targets": input.targets,
            }
            resp = await client.post("/rest/action_run", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_action_run(ctx: Context, input: GetActionRunInput) -> str:
        """Get status and results of an action run. Poll after soar_run_action. Result data is in result_data[0].data."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/action_run/{input.action_run_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_action_runs(ctx: Context, input: ListActionRunsInput) -> str:
        """List action runs, optionally filtered by container ID."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.container_id is not None:
                params.update(_filter("container", input.container_id))
            resp = await client.get("/rest/action_run", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=DESTRUCTIVE)
    async def soar_cancel_action_run(ctx: Context, input: CancelActionRunInput) -> str:
        """Cancel a running action. This stops execution — cannot be undone."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.post(f"/rest/action_run/{input.action_run_id}/cancel")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
