import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _pagination_params
from ..models.inputs import (
    GetIndicatorArtifactsInput,
    GetIndicatorByValueInput,
    GetIndicatorInput,
    GetTopIndicatorsInput,
    ListIndicatorsInput,
)

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_indicators(ctx: Context, input: ListIndicatorsInput) -> str:
        """List threat indicators aggregated across containers. Shows open/total events, severity counts."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = {
                **_pagination_params(input.limit, input.page),
                "_special_fields": "true",
                "_special_labels": "true",
                "_special_contains": "true",
                "_special_severity": "true",
            }
            if input.timerange:
                params["timerange"] = input.timerange
            if input.sort:
                params["sort"] = input.sort
            resp = await client.get("/rest/indicator", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_indicator(ctx: Context, input: GetIndicatorInput) -> str:
        """Get details for a single indicator including open_events, severity counts, and time range."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/indicator/{input.indicator_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_indicator_by_value(ctx: Context, input: GetIndicatorByValueInput) -> str:
        """Look up an indicator by its value (IP, hash, domain, etc.)."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(
                "/rest/indicator_by_value",
                params={"indicator_value": input.indicator_value},
            )
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_indicator_artifacts(ctx: Context, input: GetIndicatorArtifactsInput) -> str:
        """Get all artifacts that share a given indicator. Useful for cross-container correlation."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = {
                **_pagination_params(input.limit, input.page),
                "indicator_id": input.indicator_id,
            }
            resp = await client.get("/rest/indicator_artifact", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_top_indicators(ctx: Context, input: GetTopIndicatorsInput) -> str:
        """Get the most frequently seen indicators (IOCs) across all containers."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            resp = await client.get("/rest/top_indicator", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
