import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _pagination_params
from ..models.inputs import (
    CreateListInput,
    GetListFormattedInput,
    GetListInput,
    ListAllListsInput,
    UpdateListInput,
)

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}
WRITE_IDEMPOTENT = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_all_lists(ctx: Context, input: ListAllListsInput) -> str:
        """List all custom lists (decided_lists) with names and IDs."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            resp = await client.get("/rest/decided_list", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_list(ctx: Context, input: GetListInput) -> str:
        """Get a custom list's content (2D array) by name or ID."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/decided_list/{input.name_or_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_list_formatted(ctx: Context, input: GetListFormattedInput) -> str:
        """Get a custom list as delimited text (useful for display)."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/decided_list/{input.name}/formatted_content")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=WRITE_IDEMPOTENT)
    async def soar_update_list(ctx: Context, input: UpdateListInput) -> str:
        """Update a custom list: append rows, delete rows by index, or update specific rows. Cannot delete all rows — at least one must remain."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body: dict = {}
            if input.append_rows:
                body["append_rows"] = input.append_rows
            if input.delete_rows:
                body["delete_rows"] = input.delete_rows
            if input.update_rows:
                body["update_rows"] = input.update_rows

            if not body:
                return "No update operations specified. Provide append_rows, delete_rows, or update_rows."

            resp = await client.post(f"/rest/decided_list/{input.name_or_id}", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=WRITE)
    async def soar_create_list(ctx: Context, input: CreateListInput) -> str:
        """Create a new custom list with a name and initial content (2D array of rows)."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body = {"name": input.name, "content": input.content}
            resp = await client.post("/rest/decided_list", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
