import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _pagination_params
from ..models.inputs import GetAppActionsInput, ListAppsInput

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_system_info(ctx: Context) -> str:
        """Get SOAR system info: version, hostname, product, license details. Use to verify connectivity."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get("/rest/system_info")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_apps(ctx: Context, input: ListAppsInput) -> str:
        """List installed SOAR apps with their supported action types."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            resp = await client.get("/rest/app", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_container_options(ctx: Context) -> str:
        """Get valid values for container status, severity, label, and sensitivity fields."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get("/rest/container_options")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_app_actions(ctx: Context, input: GetAppActionsInput) -> str:
        """Get actions supported by a specific SOAR app. Use soar_list_apps first to find the app ID."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/app/{input.app_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
