# -*- coding: utf-8 -*-
# @Time    : 2025/4/9 15:26
# @Author  : lys
# @FileName: order_shipping_support.py
# @Software: PyCharm


func_schema = {
    "name": "order_shipping_support",
    "type": "function",
    "description": "Handling customer inquiries related to orders and shipping, including tracking orders, refund requests, order status updates, delivery issues, return requests, and invoice requests. Commonly used for during-sale and after-sale support.",
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
            "issue_label": {
                "type": "string",
                "description": "Specific order or shipping issue category",
                "enums": ["Logistics Tracking", "Refund Status Inquiries", "Order Cancellation", "Non-receipt of Goods", "Missing Notification Emails", "Return Requests", "Shipping Information Modification", "Invoice Requests", "Refund Requests", "Incorrect Items Shipped", "Return Policy Inquiries", "Missing Components", "System Return Difficulties", "Wrong Delivery Address", "Logistics Complaints", "Partial Order Receipt", "Invoice Information Modification", "Return Cancellation", "Expedited Shipping Requests", "Shipping Cost Inquiries", "Delivery Timeframe Inquiries", "Duplicate Charges"]
            }
        },
        "required": ["issue_label"],
        "additionalProperties": False
    },
}



async def order_shipping_support(**params):
    """
    '取消订单', '没有收到货', '没有收到提醒邮件', '想要退货', '修改收货信息', '索要发票等

    Args:
        params: 包含问题信息的字典
            - issue_label: 问题标签

    Returns:
        str: 处理建议
    """
    print("------ Detected label: ", params.get("issue_label"))
    print("start support_product_issues  tool:", params)


handler =  order_shipping_support
