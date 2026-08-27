# MyTravaly MCP Server

An MCP (Model Context Protocol) server that lets AI agents search for hotels and properties across India via the MyTravaly API. Built with Python, FastMCP, and FastAPI.

## Architecture & Stack
- **Python 3.12** with **uv** for dependency management
- **MCP Framework:** Official `mcp` Python SDK via `FastMCP`
- **API Client:** `httpx` (async) with base64-encoded payloads
- **Validation:** `pydantic` v2 + `pydantic-settings`
- **Transport:** Server-Sent Events (SSE) via `FastAPI` + `uvicorn`

## How It Works

The server exposes a single MCP tool called `search_properties` that:

1. **Autocomplete** — Takes a location name (e.g. "Delhi"), encodes it as a base64 JSON payload, and calls the MyTravaly autocomplete API to resolve it to a location ID with type, latitude, and longitude.
2. **Search Hotels** — Uses the resolved location to POST a search request, returning up to 10 hotels with names, star ratings, addresses, room details, and prices.

## Setup

1. **Install uv** (if you don't have it):
   ```bash
   pip install uv
   ```

2. **Sync dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   Create a `.env` file in the project root:
   ```env
   MYTRAVALY_API_BASE_URL="https://api.mytravaly.com/web/v4"
   MYTRAVALY_VISITOR_TOKEN="your_visitor_token"
   MYTRAVALY_AUTH_TOKEN="your_auth_token"
   ```

## Running the Server

Start the MCP server on port 3000:
```bash
uv run python run_server.py
```

Verify it's running:
```bash
curl http://localhost:3000/health
# → {"status":"ok","message":"MyTravaly MCP Server is running"}
```

## Connecting an AI Client

Point any MCP-compatible client (Claude Desktop, Cursor, etc.) to:
```
http://localhost:3000/mcp/sse
```

Example config for Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mytravaly": {
      "url": "http://localhost:3000/mcp/sse"
    }
  }
}
```

## Testing

Run the unit tests (mocked API responses):
```bash
uv run pytest
```

Run a live integration test against the real API:
```bash
uv run python test_live.py
```

## Project Structure
```
src/mytravaly_mcp/
├── config.py              # Environment settings (tokens, base URL)
├── server.py              # FastAPI app with MCP SSE mount
├── schemas/
│   └── hotel.py           # Pydantic models for API requests/responses
├── services/
│   └── mytravaly_api.py   # Async HTTP client for MyTravaly APIs
└── tools/
    └── search_properties.py  # MCP tool definition
```

## Docker

Build and run with Docker:
```bash
docker build -t mytravaly-mcp .
docker run -p 3000:3000 --env-file .env mytravaly-mcp
```
