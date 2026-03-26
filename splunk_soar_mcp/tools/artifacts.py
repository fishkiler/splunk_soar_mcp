import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _filter, _pagination_params
from ..models.inputs import CreateArtifactInput, GetArtifactInput, ListArtifactsInput

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_artifacts(ctx: Context, input: ListArtifactsInput) -> str:
        """List artifacts, optionally filtered by container ID. Returns paginated results with CEF fields."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.container_id is not None:
                params.update(_filter("container_id", input.container_id))
            resp = await client.get("/rest/artifact", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=WRITE)
    async def soar_create_artifact(ctx: Context, input: CreateArtifactInput) -> str:
        """Create an artifact on a container with CEF fields. For batch creation, set run_automation=false on all but the last artifact to avoid triggering playbooks N times."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body: dict = {
                "container_id": input.container_id,
                "name": input.name,
                "label": input.label,
                "cef": input.cef,
                "run_automation": input.run_automation,
            }
            if input.cef_types:
                body["cef_types"] = input.cef_types
            if input.tags:
                body["tags"] = input.tags

            resp = await client.post("/rest/artifact", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_artifact(ctx: Context, input: GetArtifactInput) -> str:
        """Get full details for a single artifact including CEF fields and metadata."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/artifact/{input.artifact_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
