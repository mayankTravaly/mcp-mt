import httpx
import logging
import json
import base64
from datetime import datetime, timedelta
from typing import List
from mytravaly_mcp.config import settings
from mytravaly_mcp.schemas.hotel import (
    AutocompleteResponse,
    SearchHotelsResponse,
    HotelResult
)

logger = logging.getLogger(__name__)

class MyTravalyAPIClient:
    def __init__(self):
        self.base_url = settings.mytravaly_api_base_url
        self.headers = {}
        if settings.mytravaly_visitor_token:
            self.headers["visitorToken"] = settings.mytravaly_visitor_token
        if settings.mytravaly_auth_token:
            self.headers["authToken"] = settings.mytravaly_auth_token
            
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers)

    async def close(self):
        await self.client.aclose()

    async def get_location_id(self, location_name: str) -> str:
        """
        Calls the Autocomplete API to resolve a location name to an internal ID.
        """
        # TODO: Update this endpoint path and parameters according to the Apidog docs
        endpoint = "/get/requests.js"
        logger.info(f"Fetching autocomplete for location: {location_name}")
        
        try:
            payload_dict = {
                "action": "searchAutoCompleteV2",
                "searchAutoCompleteV2": {
                    "inputText": location_name,
                    "searchType": [
                        "byCity",
                        "byState",
                        "byCountry",
                        "byRandom",
                        "byPropertyName"
                    ],
                    "limit": 10
                }
            }
            payload_json = json.dumps(payload_dict)
            payload_b64 = base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")
            
            response = await self.client.get(endpoint, params={"payload": payload_b64})
            response.raise_for_status()
            
            data = AutocompleteResponse.model_validate(response.json())
            
            if not data.status or not data.data.suggestionList:
                raise ValueError(f"No suggestions found for location: {location_name}")
            
            # For simplicity, we just pick the first suggestion's ID.
            best_match = data.data.suggestionList[0]
            logger.info(f"Found location ID {best_match.id} for {best_match.label}")
            return best_match.id
            
        except Exception as e:
            logger.error(f"Error in autocomplete API: {e}")
            raise

    async def search_hotels(self, location_id: str) -> List[HotelResult]:
        """
        Calls the Search Hotels API using a location ID and returns formatted HotelResults.
        """
        endpoint = ""
        logger.info(f"Searching hotels for location ID: {location_id}")
        
        try:
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            
            payload = {
                "action": "getSearchResultListOfHotelsV2",
                "getSearchResultListOfHotelsV2": {
                    "adult": 2,
                    "children": 0,
                    "childrenAges": [],
                    "sortBy": "popular",
                    "currency": "INR",
                    "limit": 10,
                    "offset": 0,
                    "checkIn": today.strftime("%Y-%m-%d"),
                    "checkOut": tomorrow.strftime("%Y-%m-%d"),
                    "stars": [],
                    "mealPlans": [],
                    "policies": [],
                    "propertyTypes": [
                        "HOTEL", "APARTMENT", "VACATION_RENTAL", "MOTEL",
                        "BED_AND_BREAKFAST", "COUNTRY_HOUSE", "GUESTHOUSE",
                        "HOMESTAY", "FARM_STAY", "LODGE", "VILLA", "CHALET",
                        "HOSTEL", "INN", "CAPSULE_HOTEL", "CONDO_HOTEL",
                        "RESORT", "RESORT_VILLAGE", "HOUSEBOAT", "HERITAGE_STAY",
                        "DOME_HOTEL", "CO_LIVING", "COTTAGE", "HOLIDAYHOME",
                        "CAMP_SITES_TENT"
                    ],
                    "minPrice": 0,
                    "maxPrice": 300000,
                    "searchCriteria": {
                        "type": "state", 
                        # We don't have lat/lng from just the ID, but the API might ignore it if ID is present.
                        # If required, we should parse it from autocomplete, but for now ID should suffice.
                        "latitude": 0,
                        "longitude": 0,
                        "id": location_id
                    }
                }
            }
            
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data = SearchHotelsResponse.model_validate(response.json())
            
            if not data.status or not data.data.listOfProperties:
                return []

            results = []
            for prop in data.data.listOfProperties:
                details = prop.propertyDetails
                
                # Format price from the cheapest room
                room = details.rooms
                price_per_night = room.pricing.finalPrice.pricePerNight.displayAmount
                price_for_stay = room.pricing.finalPrice.priceForStay.displayAmount
                
                address_str = f"{details.address.street}, {details.address.city}, {details.address.state}"
                
                results.append(
                    HotelResult(
                        name=details.name,
                        star_rating=details.star,
                        address=address_str,
                        description=details.description[:200] + "...", # truncate description for AI brevity
                        cheapest_room_name=room.roomName,
                        price_per_night=price_per_night,
                        price_for_stay=price_for_stay
                    )
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search hotels API: {e}")
            raise
