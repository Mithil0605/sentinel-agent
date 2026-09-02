from __future__ import annotations

from .registry import ToolDefinition

CITIES = {
    "new york": ("Partly cloudy", 21),
    "london": ("Light rain", 14),
    "tokyo": ("Clear", 26),
    "mumbai": ("Humid", 30),
    "delhi": ("Sunny", 33),
    "san francisco": ("Foggy", 17),
    "sydney": ("Windy", 19),
    "berlin": ("Overcast", 13),
    "paris": ("Sunny", 18),
    "singapore": ("Thunderstorms", 29),
}


def get_weather(city: str):
    key = city.strip().lower()
    condition, temp = CITIES.get(key, ("Unknown", None))
    if temp is None:
        return {
            "city": city,
            "condition": "unavailable",
            "temperature": None,
            "message": f"Sorry, I don't have weather data for {city}.",
            "success": True,
        }
    return {
        "city": city,
        "condition": condition,
        "temperature": temp,
        "success": True,
    }


def definition() -> ToolDefinition:
    return ToolDefinition(
        name="get_weather",
        description="Get the current weather conditions and temperature for a known city.",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Name of the city, e.g. 'London'",
                }
            },
            "required": ["city"],
        },
        handler=get_weather,
    )
