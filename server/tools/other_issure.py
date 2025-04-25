# -*- coding: utf-8 -*-
# @Time    : 2025/4/9 18:37
# @Author  : lys
# @FileName: other_issure.py
# @Software: PyCharm


# -*- coding: utf-8 -*-
# @Time    : 2025/4/9 15:26
# @Author  : lys
# @FileName: order_shipping_support.py
# @Software: PyCharm


func_schema = {
    "name": "other_issure",
    "type": "function",
    "description": "Does not include issues in other tools, such as spam message processing",
    "parameters": {
        "type": "object",
        "strict": True,
        "properties": {
            "identifiers": {
                "type": ["object", "null"],
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The Stock Keeping Unit (SKU) code that identifies a product, e.g. ."
                    },
                    "model": {
                        "type": "string",
                        "description": "The product model id in specific format, e.g.'H6199'"
                    },
                    "order_id": {
                        "type": "string",
                        "description": "The Specific order id or number. "
                    }
                },
                "description": "Identifier for an order, a product or a model."
            },
              "issue_label": {"type": "string",
                           "description": "The issue label, such as '垃圾邮件'"}
        },
        "required": ["issue_label"],
        "additionalProperties": False
    },
}



async def other_issure(**params):
    """
    '垃圾邮件

    Args:
        params: 包含问题信息的字典
            - issue_label: 问题标签

    Returns:
        str: 处理建议
    """
    print("------ Detected label: ", params.get("issue_label"))
    print("start support_product_issues  tool:", params)


handler =  other_issure
