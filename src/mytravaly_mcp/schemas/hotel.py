from pydantic import BaseModel, Field
from typing import List, Optional, Any

# --- Tool Input Schemas ---

class SearchPropertiesInput(BaseModel):
    location: str = Field(..., description="The name of the city, region, or place to search for hotels (e.g., 'Guwahati', 'New Delhi').")


# --- External API Response Schemas ---

class AutocompleteSuggestion(BaseModel):
    label: str
    description: str
    type: str
    latitude: str
    longitude: str
    id: str

class AutocompleteData(BaseModel):
    suggestionList: List[AutocompleteSuggestion]

class AutocompleteResponse(BaseModel):
    status: bool
    message: str
    responseCode: int
    data: AutocompleteData


class PriceDetails(BaseModel):
    amount: float
    displayAmount: str
    currencyAmount: str
    currencySymbol: str

class PricingCategory(BaseModel):
    pricePerNight: PriceDetails
    priceForStay: PriceDetails

class Pricing(BaseModel):
    marketPrice: PricingCategory
    finalPrice: PricingCategory

class RoomDetails(BaseModel):
    roomCode: int
    roomName: str
    description: str
    maxOccupancy: int
    availableRooms: int
    pricing: Pricing

class AddressDetails(BaseModel):
    street: str
    city: str
    state: str
    postalCode: str
    country: str
    latitude: float
    longitude: float

class PropertyDetails(BaseModel):
    name: str
    type: str
    star: int
    description: str
    address: AddressDetails
    rooms: RoomDetails

class PropertyItem(BaseModel):
    hotelCode: int
    hotelId: str
    propertyDetails: PropertyDetails

class SearchData(BaseModel):
    listOfProperties: List[PropertyItem]
    limit: int
    offset: int
    numberOfResult: int

class SearchHotelsResponse(BaseModel):
    status: bool
    message: str
    responseCode: int
    data: SearchData


# --- Tool Output Schemas ---

class HotelResult(BaseModel):
    name: str = Field(..., description="Name of the hotel")
    star_rating: int = Field(..., description="Star rating of the hotel")
    address: str = Field(..., description="Full address of the hotel")
    description: str = Field(..., description="Brief description of the property")
    cheapest_room_name: str = Field(..., description="Name of the available room")
    price_per_night: str = Field(..., description="Final price per night including currency")
    price_for_stay: str = Field(..., description="Final price for the stay including currency")

class SearchPropertiesOutput(BaseModel):
    hotels: List[HotelResult]
    total_results: int
