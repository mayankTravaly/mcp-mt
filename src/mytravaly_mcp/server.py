import logging
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from pathlib import Path
from mytravaly_mcp.tools.search_properties import mcp_server
from mytravaly_mcp.services.mytravaly_api import MyTravalyAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Custom Routes (added to FastMCP server) ---

@mcp_server.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "message": "MyTravaly MCP Server is running"})

@mcp_server.custom_route("/api/search", methods=["GET"])
async def api_search(request: Request) -> JSONResponse:
    """REST endpoint for the demo UI to search hotels."""
    location = request.query_params.get("location")
    if not location:
        return JSONResponse(
            status_code=400,
            content={"status": False, "message": "location parameter required"}
        )
    
    api_client = MyTravalyAPIClient()
    try:
        suggestion = await api_client.get_location_id(location)
        hotels = await api_client.search_hotels(suggestion)
        return JSONResponse(content={
            "status": True,
            "location": suggestion.label,
            "location_type": suggestion.type,
            "total_results": len(hotels),
            "hotels": [h.model_dump() for h in hotels]
        })
    except Exception as e:
        logger.error(f"Search API error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": False, "message": str(e)}
        )
    finally:
        await api_client.close()

@mcp_server.custom_route("/", methods=["GET"])
async def demo_ui(request: Request) -> HTMLResponse:
    """Serve the demo UI."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text())

def main():
    logger.info("Starting MyTravaly MCP Server on port 3000...")
    logger.info("  Streamable HTTP (ChatGPT): /mcp")
    logger.info("  SSE (Claude/Cursor):       /sse")
    logger.info("  Demo UI:                   /")
    mcp_server.run(transport="streamable-http", mount_path="/mcp")

if __name__ == "__main__":
    main()
