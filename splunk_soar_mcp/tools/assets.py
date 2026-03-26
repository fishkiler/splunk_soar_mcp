import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _pagination_params
from ..models.inputs import GetAssetInput, ListAssetsInput

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_assets(ctx: Context, input: ListAssetsInput) -> str:
        """List configured assets. Asset names are needed for soar_run_action targets. Filter by product name or vendor."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.product_name:
                params[f"_filter_product_name__icontains"] = f'"{input.product_name}"'
            if input.product_vendor:
                params[f"_filter_product_vendor__icontains"] = f'"{input.product_vendor}"'
            resp = await client.get("/rest/asset", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_asset(ctx: Context, input: GetAssetInput) -> str:
        """Get full details for an asset including configuration and action_whitelist."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/asset/{input.asset_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
