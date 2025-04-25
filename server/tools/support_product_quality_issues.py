# -*- coding: utf-8 -*-
# @Time    : 2025/1/9 10:02
# @Author  : lys
# @FileName: support_product_issues.py
# @Software: PyCharm
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
# from server.moban.pingzhi import *
# from server.utils import *

func_schema = {
    "name": "support_product_quality_issues",
    "type": "function",
    "description": "Handle user's product problems or quality issues including power, connectivity, hardware failures, sensors, and environmental control systems. Collect the issue label and order/product identifier (if available), and determine if the user has attempted troubleshooting. Commonly used for after-sale support.",
    "parameters": {
        "type": "object",
        "strict": True,
        "properties": {
            "issue_label": {
                "type": "string",
                "description": "Specific product issue category",
                "enums": ["Power Failure", "Lighting Failure", "Bluetooth Issues", "Control Box Failure", "WiFi Issues", "Color Inaccuracy", "Water Level Detection Failure", "Camera Failure - Not Detected", "Camera Failure - Calibration Image Not Loading", "Unable to Connect to Alexa", "Thermometer Failure - Inaccurate Reading", "Dehumidification Failure", "No Mist Output", "Water Leakage", "7143ER/EA", "False Water Leakage Alarm", "Quick Shutdown After Power On - Heater", "Unable to Receive Alerts", "Adapter Failure", "Dehumidifier - Drainage Issues", "Unable to Export Data", "Bacteria and Scale"]
            },
            "has_troubleshooted": {
                "type": "boolean",
                "description": "User-performed troubleshooting attempts verification"
            },
            "has_troubleshooted_successful": {
                "type": ["boolean", "null"],
                "description": "Outcome status of troubleshooting attempts (null if not attempted)"
            },
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
            "message": {
                "type": "string", 
                "description": "User's original issue description in source language" 
            }, 
            "proof": {
                "type": "string",
                "description": "Evidentiary media such as an image or video describing the process and result of troubleshooting.", 
            }
        },
        "required": ["issue_label", "has_troubleshooted", "message"], 
        "additionalProperties": False
    }
}

@dataclass
class SupportRequest:
    """支持请求数据类"""
    issue_label: str
    has_troubleshooted: bool
    has_troubleshooted_successful: bool
    proof: Optional[str]
    message: str
    order_id: Optional[str]
    model: Optional[str]
    sku: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupportRequest':
        identifier = data.get("identifiers")

        return cls(
            issue_label=data.get("issue_label"),
            has_troubleshooted=data.get("has_troubleshooted", False),
            has_troubleshooted_successful=data.get("has_troubleshooted_successful", False),
            proof=data.get("proof"),
            message=data.get("message"),
            order_id=identifier.get("order_id") if identifier else None,
            sku=identifier.get("sku") if identifier else None,
            model=identifier.get("model") if identifier else None,
        )

    def get_troubleshooting_steps(message: str) -> str:
        """拍错模板"""
        if "power" in message.lower():
            return "请检查:\n1. 电源连接\n2. 电源指示灯\n3. 更换插座"
        elif "connection" in message.lower():
            return "请检查:\n1. 接口连接\n2. 连接线状态\n3. 重新连接"
        else:
            return "请尝试:\n1. 关机\n2. 等待30秒\n3. 重新启动"


class ProductSupport:
    """产品服务"""
    def handle_request(self, request: SupportRequest) -> str:
        if not request.issue_label or not request.message:
            return "请提供问题描述和问题类型"

        if not request.has_troubleshooted:
            # 发送对应意图的排错模板
            return issues_moban


        # 无订单无证明
        if not request.order_id and not request.proof:
            print(request.issue_label)
            return no_order_no_proof

        # 无订单有证明
        if not request.order_id and request.proof:
            return no_order_has_proof

        # 有订单无证明
        if request.order_id and not request.proof:
            print(request.issue_label)

            return has_order_no_proof

        # 有订单有证明
        if request.order_id and  request.proof:
            return has_order_has_proof

        # 要排错
        if request.has_troubleshooted:
            # sku 排错模板
            return issues_moban

        return f"订单号:{request.order_id}\n 技术支持会尽快处理您的问题"




async def support_product_issues(**params):
    """
    品质问题排错

    Args:
        params: 包含问题信息的字典
            - issue_label: 问题标签
            - has_troubleshooted: 是否已尝试故障排除
            - proof: 图片/视频URL
            - message: 原始消息

    Returns:
        str: 处理建议
    """

    print("------ Detected label: ", params.get("issue_label"))

    if order_id := params.get("order_id"):
        if order_info := await Order_info(order_id):
            # 更新请求参数
            params.update({
                "sku": order_info['sku'],
                "model": order_info['model'],

            })
    print("start support_product_issues  tool:", params)
    request = SupportRequest.from_dict(params)

    # 排错逻辑处理
    support = ProductSupport()
    response = support.handle_request(request)
    return response

handler =  support_product_issues