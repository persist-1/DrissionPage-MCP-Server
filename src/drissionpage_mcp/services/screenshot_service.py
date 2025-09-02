# -*- coding: utf-8 -*-
"""截图服务模块

负责各种截图功能的实现。
"""

import os
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from datetime import datetime
from DrissionPage import Chromium


class ScreenshotService:
    """截图服务
    
    负责页面截图、元素截图等功能。
    """
    
    def __init__(self, tab):
        self.tab = tab
    
    def capture_page(self, 
                    path: str = None, 
                    name: str = None, 
                    full_page: bool = False) -> str:
        """捕获页面截图
        
        Args:
            path: 保存路径，如果为None则使用默认截图目录
            name: 文件名，如果为None则使用带时间戳的默认名称
            full_page: 是否截取完整页面
            
        Returns:
            str: 截图文件路径或错误信息
        """
        try:
            from ..config.settings import get_screenshots_directory
            
            # 确定截图类型和目录
            screenshot_type = "fullpage" if full_page else "viewport"
            
            if not path:
                base_dir = get_screenshots_directory()
                path = base_dir / screenshot_type
            else:
                path = Path(path)
            
            if not name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name = f"{screenshot_type}_{timestamp}.png"
            
            # 确保路径存在
            path.mkdir(parents=True, exist_ok=True)
            
            screenshot_path = self.tab.get_screenshot(
                path=str(path), 
                name=name, 
                full_page=full_page
            )
            return screenshot_path
        except Exception as e:
            return f"截图失败: {str(e)}"
    
    def capture_element(self, 
                       xpath: str, 
                       path: str = None, 
                       name: str = None) -> str:
        """捕获指定元素的截图
        
        Args:
            xpath: 元素的XPath表达式
            path: 保存路径，如果为None则使用默认元素截图目录
            name: 文件名，如果为None则使用带时间戳的默认名称
            
        Returns:
            str: 截图文件路径或错误信息
        """
        try:
            from ..config.settings import get_screenshots_directory
            
            element = self.tab.ele(f'xpath:{xpath}', timeout=4)
            
            if not element:
                return f"元素 {xpath} 不存在，无法截图"
            
            if not path:
                base_dir = get_screenshots_directory()
                path = base_dir / "element"
            else:
                path = Path(path)
            
            if not name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name = f"element_{timestamp}.png"
            
            # 确保路径存在
            path.mkdir(parents=True, exist_ok=True)
            
            screenshot_path = element.get_screenshot(path=str(path), name=name)
            return screenshot_path
        except Exception as e:
            return f"元素截图失败: {str(e)}"
    
    def capture_with_timestamp(self, 
                              path: str = None, 
                              prefix: str = "screenshot", 
                              full_page: bool = False) -> str:
        """捕获带时间戳的截图
        
        Args:
            path: 保存路径，如果为None则使用默认截图目录
            prefix: 文件名前缀
            full_page: 是否截取完整页面
            
        Returns:
            str: 截图文件路径或错误信息
        """
        try:
            # 生成时间戳文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            
            return self.capture_page(path, filename, full_page)
        except Exception as e:
            return f"时间戳截图失败: {str(e)}"
    
    def capture_viewport(self, 
                        path: str = None, 
                        name: str = None) -> str:
        """捕获当前视口截图
        
        Args:
            path: 保存路径，如果为None则使用默认视口截图目录
            name: 文件名，如果为None则使用带时间戳的默认名称
            
        Returns:
            str: 截图文件路径或错误信息
        """
        return self.capture_page(path, name, full_page=False)
    
    def capture_full_page(self, 
                         path: str = None, 
                         name: str = None) -> str:
        """捕获完整页面截图
        
        Args:
            path: 保存路径，如果为None则使用默认完整页面截图目录
            name: 文件名，如果为None则使用带时间戳的默认名称
            
        Returns:
            str: 截图文件路径或错误信息
        """
        return self.capture_page(path, name, full_page=True)
    
    def get_screenshot_bytes(self, format: str = 'jpeg') -> bytes:
        """获取截图的二进制数据
        
        Args:
            format: 图片格式，支持 'jpeg', 'png'
            
        Returns:
            bytes: 截图的二进制数据
        """
        try:
            screenshot = self.tab.get_screenshot(as_bytes=format)
            return screenshot
        except Exception as e:
            raise Exception(f"获取截图二进制数据失败: {str(e)}")
    
    def capture_multiple_elements(self, 
                                 xpaths: list, 
                                 path: str = ".", 
                                 prefix: str = "element") -> Dict[str, str]:
        """批量捕获多个元素的截图
        
        Args:
            xpaths: 元素XPath列表
            path: 保存路径
            prefix: 文件名前缀
            
        Returns:
            dict: 每个元素的截图结果
        """
        results = {}
        
        for i, xpath in enumerate(xpaths):
            filename = f"{prefix}_{i+1}.png"
            result = self.capture_element(xpath, path, filename)
            results[xpath] = result
        
        return results
    
    def capture_comparison(self, 
                          before_action: callable, 
                          after_action: callable, 
                          path: str = ".", 
                          prefix: str = "comparison") -> Dict[str, str]:
        """捕获操作前后的对比截图
        
        Args:
            before_action: 操作前的截图动作
            after_action: 操作后的截图动作
            path: 保存路径
            prefix: 文件名前缀
            
        Returns:
            dict: 对比截图结果
        """
        try:
            # 操作前截图
            before_name = f"{prefix}_before.png"
            before_result = self.capture_page(path, before_name)
            
            # 执行操作
            if before_action:
                before_action()
            
            # 等待页面稳定
            self.tab.wait(1)
            
            # 执行后续操作
            if after_action:
                after_action()
            
            # 操作后截图
            after_name = f"{prefix}_after.png"
            after_result = self.capture_page(path, after_name)
            
            return {
                "before": before_result,
                "after": after_result
            }
        except Exception as e:
            return {
                "error": f"对比截图失败: {str(e)}"
            }
    
    def capture_scroll_sequence(self, 
                               path: str = ".", 
                               prefix: str = "scroll", 
                               scroll_count: int = 5) -> List[str]:
        """捕获滚动序列截图
        
        Args:
            path: 保存路径
            prefix: 文件名前缀
            scroll_count: 滚动次数
            
        Returns:
            list: 截图文件路径列表
        """
        try:
            screenshots = []
            
            # 滚动到顶部
            self.tab.scroll.to_top()
            self.tab.wait(0.5)
            
            # 获取页面高度
            page_height = self.tab.run_js("return document.body.scrollHeight")
            viewport_height = self.tab.run_js("return window.innerHeight")
            
            if page_height <= viewport_height:
                # 页面不需要滚动
                screenshot_path = self.capture_page(path, f"{prefix}_0.png")
                screenshots.append(screenshot_path)
                return screenshots
            
            # 计算滚动步长
            scroll_step = (page_height - viewport_height) / (scroll_count - 1)
            
            for i in range(scroll_count):
                # 截图
                filename = f"{prefix}_{i}.png"
                screenshot_path = self.capture_page(path, filename)
                screenshots.append(screenshot_path)
                
                # 滚动（除了最后一次）
                if i < scroll_count - 1:
                    scroll_position = int(scroll_step * (i + 1))
                    self.tab.scroll.to_location(0, scroll_position)
                    self.tab.wait(0.5)
            
            return screenshots
        except Exception as e:
            return [f"滚动序列截图失败: {str(e)}"]
    
    def get_screenshot_info(self, file_path: str) -> Dict[str, Any]:
        """获取截图文件信息
        
        Args:
            file_path: 截图文件路径
            
        Returns:
            dict: 截图文件信息
        """
        try:
            from PIL import Image
            
            path = Path(file_path)
            
            if not path.exists():
                return {"error": f"截图文件不存在: {file_path}"}
            
            # 获取文件基本信息
            stat = path.stat()
            
            # 获取图片信息
            with Image.open(file_path) as img:
                width, height = img.size
                format = img.format
                mode = img.mode
            
            return {
                "name": path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "width": width,
                "height": height,
                "format": format,
                "mode": mode,
                "aspect_ratio": round(width / height, 2) if height > 0 else 0
            }
        except Exception as e:
            return {"error": f"获取截图信息失败: {str(e)}"}
    
    def cleanup_old_screenshots(self, 
                               path: str, 
                               days_old: int = 7, 
                               pattern: str = "*.png") -> Dict[str, Any]:
        """清理旧的截图文件
        
        Args:
            path: 截图目录路径
            days_old: 删除多少天前的文件
            pattern: 文件匹配模式
            
        Returns:
            dict: 清理结果
        """
        try:
            import time
            
            path_obj = Path(path)
            if not path_obj.exists():
                return {"error": f"路径不存在: {path}"}
            
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            deleted_files = []
            total_size_freed = 0
            
            for file_path in path_obj.glob(pattern):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files.append(str(file_path))
                    total_size_freed += file_size
            
            return {
                "deleted_count": len(deleted_files),
                "deleted_files": deleted_files,
                "size_freed_mb": round(total_size_freed / (1024 * 1024), 2)
            }
        except Exception as e:
            return {"error": f"清理截图文件失败: {str(e)}"}