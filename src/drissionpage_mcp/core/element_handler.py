# -*- coding: utf-8 -*-
"""元素处理模块

负责网页元素的查找、点击、输入等操作。
"""

from typing import Dict, Any, List, Optional, Union
from DrissionPage import Chromium
from DrissionPage.common import Keys


class ElementHandler:
    """元素处理器
    
    负责网页元素的各种操作，包括查找、点击、输入等。
    """
    
    def __init__(self, tab):
        self.tab = tab
    
    def click_by_xpath(self, xpath: str) -> Dict[str, Any]:
        """通过XPath点击元素
        
        Args:
            xpath: 元素的XPath表达式
            
        Returns:
            dict: 点击结果
        """
        locator = f"xpath:{xpath}"
        element = self.tab.ele(locator, timeout=4)
        
        if element:
            element.click()
            return {"locator": locator, "result": "点击成功"}
        else:
            return {"error": f"元素{locator}不存在，需要先获取元素信息"}
    
    def click_by_containing_text(self, content: str, index: Optional[int] = None) -> str:
        """根据包含指定文本的方式点击网页元素
        
        Args:
            content: 要查找的文本内容
            index: 当匹配到多个元素时指定要点击的索引，默认不指定
            
        Returns:
            str: 点击结果说明，或错误提示
        """
        # 获取包含指定文本的所有元素，等待最多 3 秒
        elements = self.tab.eles(content, timeout=3)

        # 如果没有匹配到任何元素，返回错误提示
        if len(elements) == 0:
            return f"元素{content}不存在，需要先获取元素信息"
        
        # 如果只找到一个元素，直接点击它
        if len(elements) == 1:
            elements[0].click()
            return "点击成功"
        
        # 如果找到多个元素
        if len(elements) > 1:
            # 如果未指定 index，提示用户提供索引
            if index is None:
                element_info = [f"索引{i}: {elem.tag} - {elem.text[:50]}" for i, elem in enumerate(elements)]
                return f"元素{content}存在多个，请调整 index 参数，index=0表示第一个元素。\n可选元素：\n" + "\n".join(element_info)
            else:
                # 根据指定索引点击对应的元素
                if 0 <= index < len(elements):
                    elements[index].click()
                    return "点击成功"
                else:
                    return f"索引{index}超出范围，共有{len(elements)}个元素"
    
    def input_by_xpath(self, xpath: str, input_value: str, clear_first: bool = True) -> Dict[str, Any]:
        """通过XPath给元素输入内容
        
        Args:
            xpath: 元素的XPath表达式
            input_value: 要输入的内容
            clear_first: 是否先清除已有内容，默认为True
            
        Returns:
            dict: 输入操作的结果
        """
        locator = f"xpath:{xpath}"
        element = self.tab.ele(locator, timeout=4)
        
        if element:
            result = element.input(input_value, clear=clear_first)
            return {"locator": locator, "result": result}
        else:
            return {"error": f"元素{locator}不存在，需要先获取元素信息"}
    
    def get_body_text(self) -> str:
        """获取当前标签页的body的文本内容
        
        Returns:
            str: body文本内容
        """
        body_element = self.tab('t:body')
        return body_element.text if body_element else ""
    
    def get_all_clickable_elements(self) -> List[Dict[str, Any]]:
        """获取页面所有可点击元素的信息
        
        Returns:
            list: 可点击元素信息列表
        """
        clickable_elements = []
        
        # 查找常见的可点击元素
        selectors = [
            'a',  # 链接
            'button',  # 按钮
            'input[type="button"]',  # 按钮类型的输入框
            'input[type="submit"]',  # 提交按钮
            'input[type="reset"]',  # 重置按钮
            '[onclick]',  # 有onclick事件的元素
            '[role="button"]',  # 角色为按钮的元素
        ]
        
        for selector in selectors:
            elements = self.tab.eles(f'css:{selector}')
            for i, elem in enumerate(elements):
                if elem.is_displayed():
                    clickable_elements.append({
                        'index': len(clickable_elements),
                        'tag': elem.tag,
                        'text': elem.text[:100] if elem.text else '',
                        'xpath': elem.xpath,
                        'selector': selector,
                        'attributes': {
                            'id': elem.attr('id') or '',
                            'class': elem.attr('class') or '',
                            'href': elem.attr('href') or '' if elem.tag == 'a' else ''
                        }
                    })
        
        return clickable_elements
    
    def get_all_input_elements(self) -> List[Dict[str, Any]]:
        """获取页面所有可输入元素的信息
        
        Returns:
            list: 可输入元素信息列表
        """
        input_elements = []
        
        # 查找输入元素
        selectors = [
            'input[type="text"]',
            'input[type="password"]',
            'input[type="email"]',
            'input[type="search"]',
            'input[type="url"]',
            'input[type="tel"]',
            'input[type="number"]',
            'textarea',
            'input:not([type])',  # 没有type属性的input默认为text
        ]
        
        for selector in selectors:
            elements = self.tab.eles(f'css:{selector}')
            for elem in elements:
                if elem.is_displayed():
                    input_elements.append({
                        'index': len(input_elements),
                        'tag': elem.tag,
                        'type': elem.attr('type') or 'text',
                        'placeholder': elem.attr('placeholder') or '',
                        'value': elem.value or '',
                        'xpath': elem.xpath,
                        'attributes': {
                            'id': elem.attr('id') or '',
                            'name': elem.attr('name') or '',
                            'class': elem.attr('class') or ''
                        }
                    })
        
        return input_elements
    
    def get_element_by_xpath(self, xpath: str) -> Optional[Dict[str, Any]]:
        """通过XPath获取元素信息
        
        Args:
            xpath: 元素的XPath表达式
            
        Returns:
            dict: 元素信息，如果不存在则返回None
        """
        element = self.tab.ele(f'xpath:{xpath}', timeout=2)
        
        if element:
            return {
                'tag': element.tag,
                'text': element.text,
                'xpath': element.xpath,
                'is_displayed': element.is_displayed(),
                'attributes': {
                    'id': element.attr('id') or '',
                    'class': element.attr('class') or '',
                    'name': element.attr('name') or ''
                }
            }
        return None
    
    def scroll_to_element(self, xpath: str) -> Dict[str, Any]:
        """滚动到指定元素
        
        Args:
            xpath: 元素的XPath表达式
            
        Returns:
            dict: 滚动结果
        """
        element = self.tab.ele(f'xpath:{xpath}', timeout=4)
        
        if element:
            element.scroll.to_see()
            return {"result": "滚动成功"}
        else:
            return {"error": f"元素{xpath}不存在"}
    
    def send_keys(self, keys: str) -> str:
        """发送键盘按键
        
        Args:
            keys: 要发送的按键
            
        Returns:
            str: 发送结果
        """
        try:
            # 将字符串转换为Keys对象
            if hasattr(Keys, keys.upper()):
                key_obj = getattr(Keys, keys.upper())
                self.tab.actions.key_down(key_obj).key_up(key_obj)
                return f"发送按键 {keys} 成功"
            else:
                # 如果不是特殊按键，直接发送字符
                self.tab.actions.type(keys)
                return f"输入文本 {keys} 成功"
        except Exception as e:
            return f"发送按键失败: {str(e)}"