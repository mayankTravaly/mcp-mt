# MyTravaly MCP Server

MCP (Model Context Protocol) server that lets AI agents search hotels via the MyTravaly API.

---

## Quick Start (Local Setup)

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
# 1. Install uv
pip install uv
# 2. Install dependencies
uv sync

# 3. Create .env file with API credentials
cat > .env << 'EOF'
MYTRAVALY_API_BASE_URL="https://api.mytravaly.com/web/v4"
MYTRAVALY_VISITOR_TOKEN="edaf-9dd8-0b4c-0923-39b1-4bde-2238-0e76"
MYTRAVALY_AUTH_TOKEN="fdd96becb0409c45581e020f9d58fc85"
EOF

# 4. Start the server
uv run python run_server.py
```

Server starts at **http://localhost:3000**

| URL | Purpose |
|-----|---------|
| http://localhost:3000 | Demo UI — search hotels visually |
| http://localhost:3000/health | Health check |
| http://localhost:3000/mcp/sse | MCP SSE endpoint for AI clients |
| http://localhost:3000/api/search?location=Delhi | REST API |

---

## How It Works

```
User/AI → "Find hotels in Delhi"
            │
            ▼
   ┌─────────────────┐
   │  MCP Server      │  localhost:3000
   │  (FastAPI + SSE)  │
   └────────┬─────────┘
            │
   Step 1:  │  GET /get/requests.js?payload=<base64>
            ▼
   ┌─────────────────┐
   │  Autocomplete    │  → Resolves "Delhi" to id=238487, type=city
   │  API             │
   └────────┬─────────┘
            │
   Step 2:  │  POST / (JSON body with searchCriteria)
            ▼
   ┌─────────────────┐
   │  Search Hotels   │  → Returns hotels with prices, rooms, ratings
   │  API             │
   └─────────────────┘
```

**Tool exposed:** `search_properties(location: str)` — takes a city name, returns hotels with prices in ₹.

---

## Connect AI Clients

Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mytravaly": {
      "url": "http://localhost:3000/mcp/sse"
    }
  }
}
```

---

## Testing

```bash
# Unit tests (mocked)
uv run pytest

# Live API test
PYTHONPATH=src uv run python test_live.py
```

---

## Project Structure
```
src/mytravaly_mcp/
├── config.py                # .env settings (tokens, base URL)
├── server.py                # FastAPI app + MCP SSE mount + demo UI
├── static/index.html        # Demo UI
├── schemas/hotel.py         # Pydantic models
├── services/mytravaly_api.py  # API client (autocomplete + search)
└── tools/search_properties.py # MCP tool definition
```

## Tech Stack
- **Python 3.12** / **uv** / **FastAPI** / **uvicorn**
- **MCP SDK** (`mcp` + `FastMCP`) with SSE transport
- **httpx** (async HTTP) / **pydantic** v2
