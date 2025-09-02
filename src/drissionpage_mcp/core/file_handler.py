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
    
    def save_screenshot(self, screenshot_data: bytes = None, path: str = None, name: str = None, screenshot_type: str = "viewport") -> str:
        """保存截图
        
        Args:
            screenshot_data: 截图数据，如果为None则直接截图
            path: 保存路径
            name: 文件名
            screenshot_type: 截图类型 (viewport, fullpage, element)
            
        Returns:
            str: 保存的文件路径
        """
        try:
            from datetime import datetime
            
            if not path:
                # 使用新的目录结构
                path = Path("screenshots") / screenshot_type
            else:
                path = Path(path)
                
            if not name:
                name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                
            # 确保目录存在
            path.mkdir(parents=True, exist_ok=True)
            
            if screenshot_data:
                # 保存提供的截图数据
                file_path = path / name
                with open(file_path, 'wb') as f:
                    f.write(screenshot_data)
                return str(file_path)
            else:
                # 直接截图并保存
                screenshot_path = self.tab.get_screenshot(path=str(path), name=name)
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
    
    def save_full_page_screenshot(self, path: str = None, name: str = None) -> str:
        """保存整个页面的截图（包括需要滚动的部分）
        
        Args:
            path: 截图保存路径
            name: 截图文件名
            
        Returns:
            str: 截图的文件路径
        """
        try:
            from datetime import datetime
            
            if not path:
                path = Path("screenshots") / "fullpage"
            else:
                path = Path(path)
                
            if not name:
                name = f"fullpage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # 确保路径存在
            path.mkdir(parents=True, exist_ok=True)
            
            # 获取完整页面截图
            screenshot_path = self.tab.get_screenshot(path=str(path), name=name, full_page=True)
            return screenshot_path
        except Exception as e:
            return f"保存完整页面截图失败: {str(e)}"
    
    def save_element_screenshot(self, xpath: str, path: str = None, name: str = None) -> str:
        """保存指定元素的截图
        
        Args:
            xpath: 元素的XPath表达式
            path: 截图保存路径
            name: 截图文件名
            
        Returns:
            str: 截图的文件路径或错误信息
        """
        try:
            from datetime import datetime
            
            element = self.tab.ele(f'xpath:{xpath}', timeout=4)
            
            if element:
                if not path:
                    path = Path("screenshots") / "element"
                else:
                    path = Path(path)
                    
                if not name:
                    name = f"element_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                
                # 确保路径存在
                path.mkdir(parents=True, exist_ok=True)
                
                screenshot_path = element.get_screenshot(path=str(path), name=name)
                return screenshot_path
            else:
                return f"元素 {xpath} 不存在，无法截图"
        except Exception as e:
            return f"保存元素截图失败: {str(e)}"
    
    def save_page_source(self, filename: str = None) -> str:
        """保存页面源码到文件
        
        Args:
            filename: 文件名，如果为None则使用默认名称
            
        Returns:
            str: 保存结果信息
        """
        try:
            from datetime import datetime
            from ..config.settings import get_page_source_directory
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"page_source_{timestamp}.html"
            
            # 使用新的页面源码目录
            page_source_dir = get_page_source_directory()
            file_path = page_source_dir / filename
            
            # 获取页面源码
            page_source = self.tab.html
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_source)
                
            return f"页面源码已保存到: {file_path}"
        except Exception as e:
            return f"保存页面源码失败: {str(e)}"
    
    def save_cookies(self, path: str = None, name: str = None) -> str:
        """保存当前页面的Cookies
        
        Args:
            path: 保存路径，如果为None则使用默认cookies目录
            name: 文件名，如果为None则使用带时间戳的默认名称
            
        Returns:
            str: 保存的文件路径或错误信息
        """
        try:
            import json
            from datetime import datetime
            
            if not path:
                # 使用新的目录结构
                path = Path("data") / "cookies"
            else:
                path = Path(path)
                
            if not name:
                name = f"cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 确保路径存在
            path.mkdir(parents=True, exist_ok=True)
            
            # 获取cookies
            cookies = self.tab.cookies()
            
            # 构建完整文件路径
            file_path = path / name
            
            # 保存cookies
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
        except Exception as e:
            return f"保存Cookies失败: {str(e)}"
    
    def load_cookies(self, filename: str = None) -> str:
        """从文件加载cookies
        
        Args:
            filename: cookies文件名，如果为None则尝试加载最新的cookies文件
            
        Returns:
            str: 加载结果信息
        """
        try:
            import json
            
            cookies_dir = Path("data") / "cookies"
            
            if not filename:
                # 查找最新的cookies文件
                cookie_files = list(cookies_dir.glob("cookies_*.json"))
                if not cookie_files:
                    return "未找到任何cookies文件"
                # 按修改时间排序，取最新的
                filename = max(cookie_files, key=lambda x: x.stat().st_mtime).name
            
            file_path = cookies_dir / filename
            
            if not file_path.exists():
                return f"Cookies文件不存在: {file_path}"
                
            with open(file_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                
            # 设置cookies到当前标签页
            for cookie in cookies:
                self.tab.set.cookies(cookie)
                
            return f"Cookies已从 {file_path} 加载成功，共 {len(cookies)} 个"
        except Exception as e:
            return f"加载cookies失败: {str(e)}"
    
    def download_file(self, url: str, save_path: str = None, filename: Optional[str] = None) -> str:
        """下载文件
        
        Args:
            url: 文件下载链接
            save_path: 保存路径，如果为None则使用默认下载目录
            filename: 文件名，如果不指定则从URL中提取
            
        Returns:
            str: 下载结果信息
        """
        try:
            import requests
            from urllib.parse import urlparse
            from ..config.settings import get_downloads_directory
            
            # 如果没有指定保存路径，使用默认下载目录
            if not save_path:
                save_path = get_downloads_directory()
            else:
                save_path = Path(save_path)
            
            # 确保保存路径存在
            save_path.mkdir(parents=True, exist_ok=True)
            
            # 如果没有指定文件名，从URL中提取
            if not filename:
                parsed_url = urlparse(url)
                filename = Path(parsed_url.path).name
                if not filename:
                    filename = "downloaded_file"
            
            # 构建完整文件路径
            file_path = save_path / filename
            
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