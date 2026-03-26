import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _filter, _pagination_params
from ..models.inputs import AddCommentInput, ListCommentsInput

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=WRITE)
    async def soar_add_comment(ctx: Context, input: AddCommentInput) -> str:
        """Add a simple text comment to a container. For structured findings, use soar_add_note instead."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body = {
                "container_id": input.container_id,
                "comment": input.comment,
            }
            resp = await client.post("/rest/container_comment", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_comments(ctx: Context, input: ListCommentsInput) -> str:
        """List comments on containers, optionally filtered by container ID."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.container_id is not None:
                params.update(_filter("container_id", input.container_id))
            resp = await client.get("/rest/container_comment", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
