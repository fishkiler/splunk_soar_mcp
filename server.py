from mcp.server.fastmcp import FastMCP

from splunk_soar_mcp.client import app_lifespan
from splunk_soar_mcp.tools import (
    actions,
    approvals,
    artifacts,
    assets,
    comments,
    containers,
    indicators,
    lists,
    notes,
    playbooks,
    system,
)

import os
import sys

_transport = os.getenv("MCP_TRANSPORT", "sse")
_host = os.getenv("MCP_HOST", "0.0.0.0")
_port = int(os.getenv("MCP_PORT", "8008"))

mcp = FastMCP(
    "Splunk SOAR",
    instructions="MCP server for Splunk SOAR On-Prem REST API — containers, artifacts, playbooks, actions, indicators, and more",
    host=_host,
    port=_port,
    lifespan=app_lifespan,
)

# Register all tool modules
system.register(mcp)
containers.register(mcp)
artifacts.register(mcp)
playbooks.register(mcp)
actions.register(mcp)
indicators.register(mcp)
notes.register(mcp)
comments.register(mcp)
lists.register(mcp)
approvals.register(mcp)
assets.register(mcp)

if __name__ == "__main__":
    mcp.run(transport=_transport)
