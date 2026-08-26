import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import json
from mytravaly_mcp.tools.search_properties import search_properties

async def main():
    print("🌍 Testing MyTravaly API integration...")
    try:
        # We will search for hotels in New Delhi
        location = "New Delhi"
        print(f"🔍 Searching for properties in '{location}'...")
        
        # Call the exact tool function that the AI would call
        result_json = await search_properties(location)
        
        # Parse and print the results nicely
        results = json.loads(result_json)
        
        if "Error" in result_json:
            print("\n❌ Error encountered:")
            print(result_json)
            return

        print(f"\n✅ Success! Found {results.get('total_results')} hotels in {location}.")
        print("-" * 50)
        
        for hotel in results.get("hotels", [])[:3]:  # Print first 3 hotels
            print(f"🏨 Name: {hotel['name']} ({hotel['star_rating']} Stars)")
            print(f"📍 Address: {hotel['address']}")
            print(f"💰 Price: {hotel['price_per_night']} per night")
            print("-" * 50)
            
    except Exception as e:
        print(f"\n❌ Script Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
