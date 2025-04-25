func_schema = {
    "name": "get_current_time",
    "description": "Get the current time in a given location",
    "type": "function",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. San Francisco",
            },
        },
        "required": ["location"],
    },
}


async def get_current_time(location):
    return f"2024-12-25 10:00:00"


handler = get_current_time
