# -*- coding: utf-8 -*-
"""DOM服务模块

负责DOM树的获取、解析和处理。
"""

from typing import Dict, Any, Optional, List
from DrissionPage import Chromium


class DOMService:
    """DOM服务
    
    负责DOM树的各种操作和处理。
    """
    
    def __init__(self, tab):
        self.tab = tab
        self._dom_tree_script = self._get_dom_tree_script()
    
    def _get_dom_tree_script(self) -> str:
        """获取DOM树转JSON的JavaScript代码
        
        Returns:
            str: JavaScript代码
        """
        return '''
        function isVisuallyHidden(node) {
          if (!(node instanceof Element)) return true;

          const invisibleTags = ['script', 'style', 'meta', 'link', 'template', 'noscript'];
          const tagName = node.nodeName.toLowerCase();

          if (invisibleTags.includes(tagName)) return true;

          const style = getComputedStyle(node);
          const hiddenByStyle = (
            style.display === 'none' ||
            style.visibility === 'hidden' ||
            style.opacity === '0'
          );

          const hasNoSize = node.offsetWidth === 0 && node.offsetHeight === 0;

          return hiddenByStyle || hasNoSize;
        }

        function domTreeToJson(node = document.body, tagCounters = {}) {
          const getNodeLabel = (node) => {
            let name = node.nodeName.toLowerCase();
            if (node.id) name += `#${node.id}`;
            if (node.className && typeof node.className === 'string') {
              const classList = node.className.trim().split(/\\s+/).join('.');
              if (classList) name += `.${classList}`;
            }
            const text = node.textContent?.trim().replace(/\\s+/g, ' ') || '';
            const content = text ? ` content='${text.slice(0, 5)}${text.length > 5 ? "…" : ""}'` : '';
            return `${name}/` + content;
          };

          if (isVisuallyHidden(node)) {
            return {}; // 过滤不可见节点
          }

          const tagName = node.nodeName.toLowerCase();
          tagCounters[tagName] = (tagCounters[tagName] || 0);
          const nodeKey = `${tagName}${tagCounters[tagName]++}`;

          const children = Array.from(node.children)
            .map(child => domTreeToJson(child, tagCounters))
            .filter(childJson => Object.keys(childJson).length > 0); // 去掉空节点

          if (children.length === 0) {
            return { [nodeKey]: getNodeLabel(node) };
          } else {
            const childJson = {};
            children.forEach(child => Object.assign(childJson, child));
            return { [nodeKey]: childJson };
          }
        }

        function buildDomJsonTree(root = document.body) {
          const topTag = root.nodeName.toLowerCase();
          const result = {};
          result[topTag] = domTreeToJson(root);
          return result;
        }

        // 用法示例
        const domJson = buildDomJsonTree();
        return JSON.stringify(domJson, null, 2);
        '''
    
    def get_simplified_dom_tree(self) -> Dict[str, Any]:
        """获取当前标签页的简化版DOM树
        
        Returns:
            dict: DOM树的JSON表示
        """
        try:
            dom_tree_json = self.tab.run_js(self._dom_tree_script)
            
            # 如果返回的是字符串，尝试解析为JSON
            if isinstance(dom_tree_json, str):
                import json
                return json.loads(dom_tree_json)
            
            return dom_tree_json
        except Exception as e:
            return {"error": f"获取DOM树失败: {str(e)}"}
    
    def get_dom_tree_by_selector(self, selector: str) -> Dict[str, Any]:
        """获取指定选择器的DOM树
        
        Args:
            selector: CSS选择器或XPath
            
        Returns:
            dict: DOM树的JSON表示
        """
        try:
            # 修改JavaScript代码以支持自定义根节点
            custom_script = self._dom_tree_script.replace(
                "const domJson = buildDomJsonTree();",
                f"const rootElement = document.querySelector('{selector}'); const domJson = rootElement ? buildDomJsonTree(rootElement) : {{}};"
            )
            
            dom_tree_json = self.tab.run_js(custom_script)
            
            if isinstance(dom_tree_json, str):
                import json
                return json.loads(dom_tree_json)
            
            return dom_tree_json
        except Exception as e:
            return {"error": f"获取指定选择器的DOM树失败: {str(e)}"}
    
    def get_element_info(self, xpath: str) -> Dict[str, Any]:
        """获取指定元素的详细信息
        
        Args:
            xpath: 元素的XPath表达式
            
        Returns:
            dict: 元素信息
        """
        try:
            element = self.tab.ele(f'xpath:{xpath}', timeout=2)
            
            if not element:
                return {"error": f"元素 {xpath} 不存在"}
            
            return {
                "tag": element.tag,
                "text": element.text,
                "inner_html": element.inner_html,
                "outer_html": element.outer_html,
                "xpath": element.xpath,
                "css_path": element.css_path,
                "is_displayed": element.is_displayed(),
                "is_enabled": element.is_enabled(),
                "location": {
                    "x": element.location[0] if element.location else 0,
                    "y": element.location[1] if element.location else 0
                },
                "size": {
                    "width": element.size[0] if element.size else 0,
                    "height": element.size[1] if element.size else 0
                },
                "attributes": {
                    "id": element.attr('id') or '',
                    "class": element.attr('class') or '',
                    "name": element.attr('name') or '',
                    "type": element.attr('type') or '',
                    "value": element.attr('value') or '',
                    "href": element.attr('href') or '',
                    "src": element.attr('src') or ''
                }
            }
        except Exception as e:
            return {"error": f"获取元素信息失败: {str(e)}"}
    
    def get_page_structure(self) -> Dict[str, Any]:
        """获取页面结构信息
        
        Returns:
            dict: 页面结构信息
        """
        try:
            structure_script = '''
            const structure = {
                title: document.title,
                url: window.location.href,
                domain: window.location.hostname,
                protocol: window.location.protocol,
                forms: document.forms.length,
                images: document.images.length,
                links: document.links.length,
                scripts: document.scripts.length,
                stylesheets: document.styleSheets.length,
                meta: {
                    description: document.querySelector('meta[name="description"]')?.content || '',
                    keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                    author: document.querySelector('meta[name="author"]')?.content || '',
                    viewport: document.querySelector('meta[name="viewport"]')?.content || ''
                },
                headings: {
                    h1: document.querySelectorAll('h1').length,
                    h2: document.querySelectorAll('h2').length,
                    h3: document.querySelectorAll('h3').length,
                    h4: document.querySelectorAll('h4').length,
                    h5: document.querySelectorAll('h5').length,
                    h6: document.querySelectorAll('h6').length
                },
                interactive: {
                    buttons: document.querySelectorAll('button').length,
                    inputs: document.querySelectorAll('input').length,
                    selects: document.querySelectorAll('select').length,
                    textareas: document.querySelectorAll('textarea').length
                }
            };
            return structure;
            '''
            
            return self.tab.run_js(structure_script)
        except Exception as e:
            return {"error": f"获取页面结构失败: {str(e)}"}
    
    def search_elements_by_text(self, text: str, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """根据文本内容搜索元素
        
        Args:
            text: 要搜索的文本
            tag: 限制搜索的标签类型，可选
            
        Returns:
            list: 匹配的元素列表
        """
        try:
            elements = []
            
            # 构建搜索选择器
            if tag:
                search_elements = self.tab.eles(f'tag:{tag}')
            else:
                search_elements = self.tab.eles('tag:*')
            
            for element in search_elements:
                if element.text and text.lower() in element.text.lower():
                    elements.append({
                        "tag": element.tag,
                        "text": element.text[:100],  # 限制文本长度
                        "xpath": element.xpath,
                        "attributes": {
                            "id": element.attr('id') or '',
                            "class": element.attr('class') or ''
                        }
                    })
            
            return elements
        except Exception as e:
            return [{"error": f"搜索元素失败: {str(e)}"}]
    
    def get_form_data(self, form_xpath: Optional[str] = None) -> Dict[str, Any]:
        """获取表单数据
        
        Args:
            form_xpath: 表单的XPath，如果不指定则获取页面第一个表单
            
        Returns:
            dict: 表单数据
        """
        try:
            if form_xpath:
                form = self.tab.ele(f'xpath:{form_xpath}')
            else:
                form = self.tab.ele('tag:form')
            
            if not form:
                return {"error": "未找到表单"}
            
            form_data = {
                "action": form.attr('action') or '',
                "method": form.attr('method') or 'GET',
                "fields": []
            }
            
            # 获取表单字段
            inputs = form.eles('tag:input')
            selects = form.eles('tag:select')
            textareas = form.eles('tag:textarea')
            
            all_fields = inputs + selects + textareas
            
            for field in all_fields:
                field_info = {
                    "tag": field.tag,
                    "type": field.attr('type') or '',
                    "name": field.attr('name') or '',
                    "id": field.attr('id') or '',
                    "value": field.value or '',
                    "placeholder": field.attr('placeholder') or '',
                    "required": field.attr('required') is not None,
                    "xpath": field.xpath
                }
                form_data["fields"].append(field_info)
            
            return form_data
        except Exception as e:
            return {"error": f"获取表单数据失败: {str(e)}"}