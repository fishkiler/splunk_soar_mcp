import json

import httpx
from mcp.server.fastmcp import Context, FastMCP

from ..client import _err, _filter, _pagination_params
from ..models.inputs import ListApprovalsInput, RespondToApprovalInput

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True}
WRITE = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False}


def register(mcp: FastMCP) -> None:

    @mcp.tool(annotations=READ_ONLY)
    async def soar_list_approvals(ctx: Context, input: ListApprovalsInput) -> str:
        """List approval tasks (workbook tasks). Defaults to pending approvals. Approvals use /rest/workbook_task, not the legacy /rest/approval endpoint."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            params = _pagination_params(input.limit, input.page)
            if input.status:
                params.update(_filter("status", input.status))
            resp = await client.get("/rest/workbook_task", params=params)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)

    @mcp.tool(annotations=WRITE)
    async def soar_respond_to_approval(ctx: Context, input: RespondToApprovalInput) -> str:
        """Respond to a pending approval task (approve, decline, etc.)."""
        client: httpx.AsyncClient = ctx.request_context.lifespan_context["client"]
        try:
            body = {"responses": [{"value": input.response_value}]}
            resp = await client.post(f"/rest/workbook_task/{input.task_id}", json=body)
            resp.raise_for_status()
            return json.dumps(resp.json(), indent=2)
        except Exception as e:
            return _err(e)
