import httpx
import logging
import json
import base64
from datetime import datetime, timedelta
from typing import List
from mytravaly_mcp.config import settings
from mytravaly_mcp.schemas.hotel import (
    AutocompleteResponse,
    AutocompleteSuggestion,
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
            
        # Add the Origin header as Mayank requested port 3000 to be whitelisted
        self.headers["Origin"] = "http://localhost:3000"
            
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers)

    async def close(self):
        await self.client.aclose()

    async def get_location_id(self, location_name: str) -> AutocompleteSuggestion:
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
            payload_json = json.dumps(payload_dict, separators=(',', ':'))
            payload_b64 = base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")
            
            response = await self.client.get(endpoint, params={"payload": payload_b64})
            if response.status_code >= 400:
                logger.error(f"API Error Response: {response.text}")
            response.raise_for_status()
            
            data = AutocompleteResponse.model_validate(response.json())
            
            if not data.status or not data.data.suggestionList:
                raise ValueError(f"No suggestions found for location: {location_name}")
            
            # Smart match: prefer exact label matches and city/state types over properties
            suggestions = data.data.suggestionList
            query_lower = location_name.lower()
            
            # 1. Exact label match (case-insensitive)
            best_match = next(
                (s for s in suggestions if s.label.lower() == query_lower),
                None
            )
            
            # 2. Exact match among city/state only
            if not best_match:
                best_match = next(
                    (s for s in suggestions 
                     if s.label.lower() == query_lower and s.type in ("city", "state", "country")),
                    None
                )
            
            # 3. First city/state result
            if not best_match:
                best_match = next(
                    (s for s in suggestions if s.type in ("city", "state", "country")),
                    None
                )
            
            # 4. Fall back to first result
            if not best_match:
                best_match = suggestions[0]
            
            logger.info(f"Found location: {best_match.label} (type={best_match.type}, id={best_match.id})")
            return best_match
            
        except Exception as e:
            logger.error(f"Error in autocomplete API: {e}")
            raise

    async def search_hotels(self, location: AutocompleteSuggestion) -> List[HotelResult]:
        """
        Calls the Search Hotels API using an autocomplete suggestion and returns formatted HotelResults.
        """
        endpoint = ""
        logger.info(f"Searching hotels for {location.label} (type={location.type}, id={location.id})")
        
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
                    "limit": 50,
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
                        "type": location.type,
                        "latitude": float(location.latitude),
                        "longitude": float(location.longitude),
                        "id": location.id
                    }
                }
            }
            
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            data = SearchHotelsResponse.model_validate(response.json())
            
            if not data.status or not data.data or not data.data.listOfProperties:
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
