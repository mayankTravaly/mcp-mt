import pytest
import respx
from httpx import Response
from mytravaly_mcp.services.mytravaly_api import MyTravalyAPIClient
from mytravaly_mcp.tools.search_properties import search_properties
from mytravaly_mcp.config import settings

# Dummy JSON responses directly matching the user's provided schema
AUTOCOMPLETE_MOCK_RESPONSE = {
    "status": True,
    "message": "Suggestion list fetch successfully.",
    "responseCode": 200,
    "data": {
        "suggestionList": [
            {
                "label": "Guwahati",
                "description": "Assam, India",
                "type": "city",
                "latitude": "26.1844",
                "longitude": "91.7458",
                "id": "12345"
            }
        ]
    }
}

SEARCH_MOCK_RESPONSE = {
    "status": True,
    "message": "Search result fetched successfully.",
    "responseCode": 200,
    "data": {
        "listOfProperties": [
            {
                "hotelCode": 111,
                "hotelId": "abc",
                "propertyDetails": {
                    "name": "Hotel Test View",
                    "type": "HOTEL",
                    "star": 4,
                    "description": "A very nice test hotel.",
                    "address": {
                        "street": "123 Test St",
                        "city": "Guwahati",
                        "state": "Assam",
                        "postalCode": "781001",
                        "country": "India",
                        "latitude": 26.1,
                        "longitude": 91.7
                    },
                    "rooms": {
                        "roomCode": 1,
                        "roomName": "Deluxe Test Room",
                        "description": "Awesome room",
                        "maxOccupancy": 2,
                        "availableRooms": 5,
                        "pricing": {
                            "marketPrice": {
                                "pricePerNight": {"amount": 2000.0, "displayAmount": "₹2,000", "currencyAmount": "2,000", "currencySymbol": "₹"},
                                "priceForStay": {"amount": 2000.0, "displayAmount": "₹2,000", "currencyAmount": "2,000", "currencySymbol": "₹"}
                            },
                            "finalPrice": {
                                "pricePerNight": {"amount": 1500.0, "displayAmount": "₹1,500", "currencyAmount": "1,500", "currencySymbol": "₹"},
                                "priceForStay": {"amount": 1500.0, "displayAmount": "₹1,500", "currencyAmount": "1,500", "currencySymbol": "₹"}
                            }
                        }
                    }
                }
            }
        ],
        "limit": 10,
        "offset": 0,
        "numberOfResult": 1
    }
}


@pytest.mark.asyncio
@respx.mock
async def test_search_properties_tool_success():
    # Mock the Autocomplete endpoint
    import base64, json
    
    payload_dict = {
        "action": "searchAutoCompleteV2",
        "searchAutoCompleteV2": {
            "inputText": "Guwahati",
            "searchType": ["byCity", "byState", "byCountry", "byRandom", "byPropertyName"],
            "limit": 10
        }
    }
    payload_b64 = base64.b64encode(json.dumps(payload_dict).encode("utf-8")).decode("utf-8")
    
    respx.get(url__startswith=f"{settings.mytravaly_api_base_url}/get/requests.js").mock(
        return_value=Response(200, json=AUTOCOMPLETE_MOCK_RESPONSE)
    )
    
    # Mock the Search endpoint
    respx.post(url__startswith=settings.mytravaly_api_base_url).mock(
        return_value=Response(200, json=SEARCH_MOCK_RESPONSE)
    )

    # Call the MCP tool
    result_json = await search_properties("Guwahati")
    
    assert "Hotel Test View" in result_json
    assert "₹1,500" in result_json
    assert "Deluxe Test Room" in result_json

@pytest.mark.asyncio
@respx.mock
async def test_search_properties_no_autocomplete_results():
    empty_autocomplete = {
        "status": False,
        "message": "No results",
        "responseCode": 200,
        "data": {"suggestionList": []}
    }
    
    respx.get(url__startswith=f"{settings.mytravaly_api_base_url}/get/requests.js").mock(
        return_value=Response(200, json=empty_autocomplete)
    )

    result_json = await search_properties("UnknownCity")
    
    # Tool should gracefully catch the ValueError raised by the service and return an error message
    assert "Error occurred while searching properties" in result_json
    assert "No suggestions found" in result_json
