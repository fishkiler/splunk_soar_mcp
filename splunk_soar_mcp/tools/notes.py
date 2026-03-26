import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _filter, _pagination_params
from ..models.inputs import AddNoteInput, GetNoteInput, ListNotesInput

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=WRITE)
    async def soar_add_note(ctx: Context, input: AddNoteInput) -> str:
        """Add a structured note to a container. Notes support markdown and can be attached to workbook phases. Use for analyst findings; use comments for quick annotations."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body: dict = {
                "container_id": input.container_id,
                "title": input.title,
                "content": input.content,
                "note_type": input.note_type,
            }
            if input.phase_id is not None:
                body["phase_id"] = input.phase_id

            resp = await client.post("/rest/note", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_notes(ctx: Context, input: ListNotesInput) -> str:
        """List notes, optionally filtered by container ID."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.container_id is not None:
                params.update(_filter("container_id", input.container_id))
            resp = await client.get("/rest/note", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=READ_ONLY)
    async def soar_get_note(ctx: Context, input: GetNoteInput) -> str:
        """Get a single note with full content and attachments."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            resp = await client.get(f"/rest/note/{input.note_id}")
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
