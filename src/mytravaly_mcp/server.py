import uvicorn
import logging
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from mytravaly_mcp.tools.search_properties import mcp_server
from mytravaly_mcp.services.mytravaly_api import MyTravalyAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MyTravaly MCP Server")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "MyTravaly MCP Server is running"}

@app.get("/api/search")
async def api_search(location: str = Query(..., description="City or location to search")):
    """REST endpoint for the demo UI to search hotels."""
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

@app.get("/", response_class=HTMLResponse)
async def demo_ui():
    """Serve the demo UI."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text())

# Mount the FastMCP SSE application
app.mount("/mcp", mcp_server.sse_app())

def main():
    logger.info("Starting MyTravaly MCP Server on port 3000...")
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()
