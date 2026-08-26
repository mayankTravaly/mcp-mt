import uvicorn
import logging
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.transport.sse import sse_router
from mytravaly_mcp.tools.search_properties import mcp_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MyTravaly MCP Server")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "MyTravaly MCP Server is running"}

# Mount FastMCP SSE router
app.include_router(sse_router(mcp_server), prefix="/mcp")

def main():
    logger.info("Starting MyTravaly MCP Server on port 8000...")
    # This runs the standard FastMCP server via SSE built-in
    mcp_server.run(transport='sse', port=8000)

if __name__ == "__main__":
    main()
