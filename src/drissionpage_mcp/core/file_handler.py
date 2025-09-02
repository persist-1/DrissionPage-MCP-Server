# -*- coding: utf-8 -*-
"""文件处理模块

负责截图、文件保存等文件相关操作。
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from DrissionPage import Chromium


class FileHandler:
    """文件处理器
    
    负责截图、文件保存等文件操作。
    """
    
    def __init__(self, tab):
        self.tab = tab
    
    def get_screenshot_bytes(self, format: str = 'jpeg') -> bytes:
        """获取当前标签页的网页截图二进制数据
        
        Args:
            format: 截图格式，支持 'jpeg', 'png'
            
        Returns:
            bytes: 截图的二进制数据
        """
        try:
            screenshot = self.tab.get_screenshot(as_bytes=format)
            return screenshot
        except Exception as e:
            raise Exception(f"获取截图失败: {str(e)}")
    
    def save_screenshot(self, path: str = ".", name: str = "screenshot.png") -> str:
        """获取当前标签页的屏幕截图并保存为文件
        
        Args:
            path: 截图保存路径，默认为当前目录
            name: 截图文件名，默认为screenshot.png
            
        Returns:
            str: 截图的文件路径
        """
        try:
            # 确保路径存在
            Path(path).mkdir(parents=True, exist_ok=True)
            
            screenshot_path = self.tab.get_screenshot(path=path, name=name)
            return screenshot_path
        except Exception as e:
            return f"保存截图失败: {str(e)}"
    
    def save_screenshot_with_timestamp(self, path: str = ".", prefix: str = "screenshot") -> str:
        """保存带时间戳的截图
        
        Args:
            path: 截图保存路径
            prefix: 文件名前缀
            
        Returns:
            str: 截图的文件路径
        """
        try:
            from datetime import datetime
            
            # 生成时间戳文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            
            return self.save_screenshot(path, filename)
        except Exception as e:
            return f"保存时间戳截图失败: {str(e)}"
    
    def save_full_page_screenshot(self, path: str = ".", name: str = "fullpage_screenshot.png") -> str:
        """保存整个页面的截图（包括需要滚动的部分）
        
        Args:
            path: 截图保存路径
            name: 截图文件名
            
        Returns:
            str: 截图的文件路径
        """
        try:
            # 确保路径存在
            Path(path).mkdir(parents=True, exist_ok=True)
            
            # 获取完整页面截图
            screenshot_path = self.tab.get_screenshot(path=path, name=name, full_page=True)
            return screenshot_path
        except Exception as e:
            return f"保存完整页面截图失败: {str(e)}"
    
    def save_element_screenshot(self, xpath: str, path: str = ".", name: str = "element_screenshot.png") -> str:
        """保存指定元素的截图
        
        Args:
            xpath: 元素的XPath表达式
            path: 截图保存路径
            name: 截图文件名
            
        Returns:
            str: 截图的文件路径或错误信息
        """
        try:
            element = self.tab.ele(f'xpath:{xpath}', timeout=4)
            
            if element:
                # 确保路径存在
                Path(path).mkdir(parents=True, exist_ok=True)
                
                screenshot_path = element.get_screenshot(path=path, name=name)
                return screenshot_path
            else:
                return f"元素 {xpath} 不存在，无法截图"
        except Exception as e:
            return f"保存元素截图失败: {str(e)}"
    
    def save_page_source(self, path: str = ".", name: str = "page_source.html") -> str:
        """保存当前页面的HTML源码
        
        Args:
            path: 保存路径
            name: 文件名
            
        Returns:
            str: 保存的文件路径或错误信息
        """
        try:
            # 确保路径存在
            Path(path).mkdir(parents=True, exist_ok=True)
            
            # 获取页面源码
            html_content = self.tab.html
            
            # 构建完整文件路径
            file_path = Path(path) / name
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(file_path)
        except Exception as e:
            return f"保存页面源码失败: {str(e)}"
    
    def save_cookies(self, path: str = ".", name: str = "cookies.json") -> str:
        """保存当前页面的Cookies
        
        Args:
            path: 保存路径
            name: 文件名
            
        Returns:
            str: 保存的文件路径或错误信息
        """
        try:
            import json
            
            # 确保路径存在
            Path(path).mkdir(parents=True, exist_ok=True)
            
            # 获取cookies
            cookies = self.tab.cookies()
            
            # 构建完整文件路径
            file_path = Path(path) / name
            
            # 保存cookies
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
        except Exception as e:
            return f"保存Cookies失败: {str(e)}"
    
    def load_cookies(self, file_path: str) -> str:
        """从文件加载Cookies
        
        Args:
            file_path: Cookies文件路径
            
        Returns:
            str: 加载结果信息
        """
        try:
            import json
            
            # 检查文件是否存在
            if not Path(file_path).exists():
                return f"Cookies文件不存在: {file_path}"
            
            # 读取cookies
            with open(file_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 设置cookies
            for cookie in cookies:
                self.tab.set.cookies(cookie)
            
            return f"成功加载 {len(cookies)} 个Cookies"
        except Exception as e:
            return f"加载Cookies失败: {str(e)}"
    
    def download_file(self, url: str, save_path: str, filename: Optional[str] = None) -> str:
        """下载文件
        
        Args:
            url: 文件下载链接
            save_path: 保存路径
            filename: 文件名，如果不指定则从URL中提取
            
        Returns:
            str: 下载结果信息
        """
        try:
            import requests
            from urllib.parse import urlparse
            
            # 确保保存路径存在
            Path(save_path).mkdir(parents=True, exist_ok=True)
            
            # 如果没有指定文件名，从URL中提取
            if not filename:
                parsed_url = urlparse(url)
                filename = Path(parsed_url.path).name
                if not filename:
                    filename = "downloaded_file"
            
            # 构建完整文件路径
            file_path = Path(save_path) / filename
            
            # 下载文件
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return f"文件下载成功: {file_path}"
        except Exception as e:
            return f"文件下载失败: {str(e)}"
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {"error": f"文件不存在: {file_path}"}
            
            stat = path.stat()
            
            return {
                "name": path.name,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "extension": path.suffix
            }
        except Exception as e:
            return {"error": f"获取文件信息失败: {str(e)}"}