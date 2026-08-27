from mcp.server.fastmcp import FastMCP
from mytravaly_mcp.schemas.hotel import SearchPropertiesInput, SearchPropertiesOutput
from mytravaly_mcp.services.mytravaly_api import MyTravalyAPIClient
import logging

logger = logging.getLogger(__name__)

mcp_server = FastMCP("MyTravaly Search Server")

@mcp_server.tool(
    name="search_properties",
    description="Search for hotels and properties in a given location (e.g. 'New Delhi', 'Guwahati'). It returns a list of matching hotels along with their prices and details."
)
async def search_properties(location: str) -> str:
    logger.info(f"Tool called: search_properties for location '{location}'")
    
    api_client = MyTravalyAPIClient()
    try:
        # Step 1: Autocomplete to get Location details
        location_suggestion = await api_client.get_location_id(location)
        
        # Step 2: Search hotels using the full location details
        hotels = await api_client.search_hotels(location_suggestion)
        
        # Step 3: Format Output
        output = SearchPropertiesOutput(
            hotels=hotels,
            total_results=len(hotels)
        )
        
        return output.model_dump_json(indent=2)
        
    except Exception as e:
        logger.error(f"Failed to search properties: {e}")
        return f"Error occurred while searching properties: {str(e)}"
        
    finally:
        await api_client.close()
