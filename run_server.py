import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from mytravaly_mcp.server import mcp_server

# Get the native Starlette app from FastMCP
app = mcp_server.streamable_http_app()

# Add CORS middleware (required by ChatGPT for preflight OPTIONS requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

