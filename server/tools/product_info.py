func_schema = {
    "name": "product_info",
    "type": "function",
    "description": "Handle product-related inquiries from users, including questions about product features, purchase recommendations, etc. Commonly used for pre-sales and during-sales support.",
    "parameters": {
        "type": "object",
        "properties": {
            "sku": {
                "type": "string",
                "description": "The product SKU in specific format",
            },
            "issue_label": {
                "type": "string",
                "description": "Specific product issue category",
                "enums": ["Product Information Inquiries", "Product Usage Instructions", "Purchase Methods", "Product Feature Inquiries", "App Usage Guidance", "Installation Solution Inquiries", "Size/Dimension Solution Inquiries", "Purchase Recommendations", "Add-on Accessories", "Light Strip Cutting and Extension", "Restock Time Inquiries", "Discount Inquiries"]
            }
        }
    },
}



async def product_info(**params):
    import aiohttp
    import json

    sku = params.get("sku")
    query = params.get("query")

    print(f"Fetching product docs for product: {sku} with query: {query}")

    graphrag_url = "https://eap-user.zengjian.cc:9320/api/askkb/47"
    graphrag_token = "946B2E0E-4EC3-4E8D-AE7B-F4A24234AA50"
    graphrag_email = "test2@dummy.com"

    headers = {"Content-Type": "application/json", "X-Token": graphrag_token, "X-Email": graphrag_email}

    body = json.dumps({"Content": f"For product {sku}: {query}", "SessionId": ""})

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(graphrag_url, headers=headers, data=body) as response:
                result = await response.text()
                print(f"product_info result: {result}")
                return result
    except Exception as error:
        print(f"Error fetching product docs: {error}")
        return {}


handler = product_info
