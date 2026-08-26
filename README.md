# MyTravaly MCP Server

This repository contains the Model Context Protocol (MCP) server for MyTravaly, allowing AI agents to search for hotels and properties via the MyTravaly API.

## Architecture & Stack
- **Python 3.12**
- **Dependency Management:** `uv`
- **MCP Framework:** `mcp` (Official Python SDK) via `FastMCP`
- **API Client:** `httpx` (async)
- **Validation:** `pydantic` v2 and `pydantic-settings`
- **Deployment Transport:** Server-Sent Events (SSE) via `FastAPI` + `uvicorn`

## Setup Instructions

1. **Install uv** (if you don't have it):
   ```bash
   pip install uv
   ```

2. **Sync Dependencies**:
   ```bash
   uv sync
   ```

3. **Environment Variables**:
   Copy the example config and add the real Apidog URLs when available:
   ```bash
   cp .env.example .env
   ```

## Development & Testing

To run the local unit tests (which mock the API requests based on the established schemas):
```bash
uv run pytest
```

## Running the Server

To start the FastAPI SSE server locally for AI clients to connect to:
```bash
uv run python src/mytravaly_mcp/server.py
```
*or directly with uvicorn:*
```bash
uv run uvicorn mytravaly_mcp.server:app --port 8000
```

## Next Steps (Integration)
When the exact API endpoints are retrieved from Apidog:
1. Update `MYTRAVALY_API_BASE_URL` in `.env`.
2. Update the `endpoint` paths inside `src/mytravaly_mcp/services/mytravaly_api.py`.
3. If a specific authentication header key is required instead of `Bearer`, adjust the headers dictionary in `MyTravalyAPIClient.__init__`.
