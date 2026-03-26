# Splunk SOAR MCP Server

An MCP (Model Context Protocol) server that exposes the Splunk SOAR On-Prem REST API as 40 tools across 11 domains. Built with [FastMCP](https://github.com/jlowin/fastmcp), it allows AI assistants like Claude to interact with Splunk SOAR for security operations — managing containers, artifacts, playbooks, actions, indicators, and more.

## Features

- **Containers** — Create, update, list, and audit events/cases
- **Artifacts** — Manage IOCs with CEF fields, batch ingestion support
- **Playbooks** — Run, monitor, list, and cancel playbook executions
- **Actions** — Execute app actions (enrichment, containment, etc.) and poll results
- **Indicators** — Query threat indicators, cross-container correlation, top IOCs
- **Notes & Comments** — Document findings and annotate containers
- **Custom Lists** — CRUD operations on decided lists
- **Approvals** — List and respond to workbook approval tasks
- **Assets** — Browse configured assets and their supported actions
- **System** — Verify connectivity, list apps, get container field options

See [docs/tools-reference.md](docs/tools-reference.md) for the full tool catalog with parameters and example workflows.

## Requirements

- Python 3.10+
- Splunk SOAR On-Prem instance (tested on 6.4.1 / 8.4)
- SOAR API token or username/password credentials

## Installation

```bash
# Clone the repo
git clone https://github.com/fishkiler/splunk_soar_mcp.git
cd splunk_soar_mcp

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Or with uv
uv sync
```

## Configuration

Copy the example environment file and fill in your SOAR credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SOAR_HOST=https://your-soar-instance.example.com
SOAR_TOKEN=your_api_token_here
SOAR_VERIFY_SSL=false
SOAR_USER=soar_local_admin
SOAR_PASS=
```

Authentication supports either a **SOAR API token** (`SOAR_TOKEN`) or **username/password** (`SOAR_USER` / `SOAR_PASS`). Token-based auth is recommended.

## Usage

### Run with SSE transport (default)

```bash
python server.py
```

The server starts on `0.0.0.0:8008` by default. Override with environment variables:

```env
MCP_TRANSPORT=sse    # sse or stdio
MCP_HOST=0.0.0.0
MCP_PORT=8008
```

### Run with stdio transport

```bash
MCP_TRANSPORT=stdio python server.py
```

### Claude Desktop / Claude Code

Add to your MCP client config:

```json
{
  "mcpServers": {
    "splunk-soar": {
      "url": "http://<server-ip>:8008/sse"
    }
  }
}
```

Or for stdio mode:

```json
{
  "mcpServers": {
    "splunk-soar": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/splunk_soar_mcp"
    }
  }
}
```

## Project Structure

```
splunk_soar_mcp/
├── server.py                  # MCP server entrypoint
├── splunk_soar_mcp/
│   ├── client.py              # SOAR HTTP client (httpx)
│   ├── config.py              # Environment config loader
│   ├── models/
│   │   └── inputs.py          # Pydantic input models
│   └── tools/
│       ├── actions.py         # Action run/cancel/status
│       ├── approvals.py       # Approval task management
│       ├── artifacts.py       # Artifact CRUD
│       ├── assets.py          # Asset listing
│       ├── comments.py        # Container comments
│       ├── containers.py      # Container CRUD + audit
│       ├── indicators.py      # Threat indicator queries
│       ├── lists.py           # Custom list operations
│       ├── notes.py           # Container notes
│       ├── playbooks.py       # Playbook run/cancel/status
│       └── system.py          # System info, apps, options
├── docs/
│   └── tools-reference.md     # Full tool parameter reference
├── .env.example               # Environment template
└── pyproject.toml
```

## License

MIT
