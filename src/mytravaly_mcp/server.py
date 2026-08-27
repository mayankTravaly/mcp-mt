import uvicorn
import logging
from fastapi import FastAPI
from mytravaly_mcp.tools.search_properties import mcp_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MyTravaly MCP Server")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "MyTravaly MCP Server is running"}

# Mount the FastMCP SSE application
app.mount("/mcp", mcp_server.sse_app())

def main():
    logger.info("Starting MyTravaly MCP Server on port 3000...")
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    main()
