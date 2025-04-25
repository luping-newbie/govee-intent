# -*- coding: utf-8 -*-
# @Time    : 2025/1/9 09:54
# @Author  : lys
# @FileName: utils.py
# @Software: PyCharm

# 使用正则表达式定位PII数据
import re

def anonymize_text(text):
    """仅脱敏邮箱和地址，其他内容完全保留"""
    try:
        # 邮箱脱敏（保留前3字符+完整域名）
        text = re.sub(
            r'\b([a-zA-Z0-9_.+]{3})[a-zA-Z0-9_.+]*@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b',
            r'\1​**​*@\2',  # 示例：ibw​**​*@gmail.com
            text,
            flags=re.IGNORECASE
        )

        # 精确地址匹配（避免误判产品型号）
        address_regex = re.compile(r'''
            \b
            \d{1,5}\s                          # 街道号（1-5位数字）
            (?:[A-Za-z0-9#]+\s)+               # 街道名（字母/数字/#）
            (?:St(?:reet)?|Ave|Rd|Blvd|Way)    # 街道类型
            (?:,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)?  # 州和邮编（可选）
            \b
        ''', re.VERBOSE | re.IGNORECASE)

        text = address_regex.sub('[ADDR_REDACTED]', text)
        return text

    except re.error:
        return text  # 保持原始内容



if __name__ == '__main__':
    # text='''Oops typo on email, correct one below
    #
    # ibwilliams17@gmail.com'''

    text='''Oh, thank you! I was wondering what was up with it.  Here’s the info for you:
    
    Ian Williams
    ibwilliamz17@gmail.com
    6619 Roosevelt Way NE #407, Seattle WA 98115
    
    Service was great, super fast and unassuming. I appreciate it!
    '''
    text='''Hi, I’ve got a set of H6167 that isn’t responding properly to the commands in the app. It worked fine for a few days then just stopped, I’ve tried factory resetting it to no luck. It’ll either be just red which it defaults to, or really dim to another color, is there a firmware update I can do or something to fix this?'''
    text='''Hi Lisa, thanks for the super fast response. I tried your method with leaving it unplugged after a reset and no change unfortunately. Here’s a video showing me cycling through the color options on the controller and showing the inconsistent behavior. Sometimes when it’s first powered on the section closest to my thumb and the one closest to my other fingers is completely off. Order number was 113-6024349-1729810. Let me know how else I can help'''
    format_text =anonymize_text(text)
    print(format_text)