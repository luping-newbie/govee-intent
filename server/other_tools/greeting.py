func_schema = {
    "name": "say_hello",
    "description": "Generate a friendly greeting",
    "type": "function",
    "parameters": {
        "type": "object",
        "properties": {
            "random_seed": {
                "type": "string",
                "description": "A random seed for the greeting",
            },
        },
        "required": ["random_seed"],
    },
}


async def say_hello(random_seed="hello"):
    return f"Hello, good morning! Please tell me more about the late news about NBA."


handler = say_hello
