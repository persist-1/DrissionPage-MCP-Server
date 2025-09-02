# -*- coding: utf-8 -*-
"""浏览器管理模块

负责浏览器的启动、连接、标签页管理等核心功能。
"""

import os
from typing import Dict, Any, Optional
from DrissionPage import Chromium, ChromiumOptions


class BrowserManager:
    """浏览器管理器
    
    负责浏览器实例的创建、配置和管理。
    """
    
    def __init__(self):
        self.browser: Optional[Chromium] = None
        self.current_tab = None
        self._setup_chrome_path()
    
    async def connect_or_open_browser(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """打开或接管已打开的浏览器
        
        Args:
            config: 浏览器配置字典，可选键包括 debug_port、browser_path、headless
            
        Returns:
            dict: 浏览器信息
        """
        if config is None:
            config = {'debug_port': 9222}
            
        co = ChromiumOptions()
        
        if config.get("debug_port"):
            co.set_local_port(config["debug_port"])
        if config.get("browser_path"):
            co.set_browser_path(config["browser_path"])
        if config.get("headless", False):
            co.headless(True)

        self.browser = Chromium(co)
        self.current_tab = self.browser.latest_tab

        return {
            "browser_address": co.address,
            "latest_tab_title": self.current_tab.title,
            "latest_tab_id": self.current_tab.tab_id,
        }
    
    def _setup_chrome_path(self):
        """自动配置Chrome路径，优先使用便携版Chrome"""
        # 项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # 便携版Chrome路径（优先级最高）
        portable_chrome_paths = [
            os.path.join(project_root, 'browsers', 'chrome-portable', 'chrome.exe'),
            os.path.join(project_root, 'browsers', 'chrome-portable', 'GoogleChromePortable.exe'),
        ]
        
        # 系统安装的Chrome路径
        system_chrome_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME', '')),
            # Edge作为备选
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        ]
        
        # 合并路径列表，便携版优先
        all_paths = portable_chrome_paths + system_chrome_paths
        
        for path in all_paths:
            if os.path.exists(path):
                try:
                    ChromiumOptions().set_browser_path(path).save()
                    print(f"已配置浏览器路径: {path}")
                    if path in portable_chrome_paths:
                        print("✅ 使用项目内置便携版Chrome")
                    return
                except Exception as e:
                    continue
        
        print("⚠️ 未找到Chrome或Edge浏览器")
        print("请下载便携版Chrome到 browsers/chrome-portable/ 目录")
        print("或安装系统版Chrome浏览器")
    
    async def new_tab(self, url: str) -> Dict[str, Any]:
        """打开新标签页并访问指定网址
        
        Args:
            url: 要访问的网址
            
        Returns:
            dict: 标签页信息
        """
        if not self.browser:
            await self.connect_or_open_browser()
            
        tab = self.browser.new_tab(url)
        self.current_tab = tab
        
        return {
            "title": tab.title,
            "tab_id": tab.tab_id,
            "url": tab.url
        }
    
    async def get(self, url: str) -> Dict[str, Any]:
        """在当前标签页打开网址
        
        Args:
            url: 要访问的网址
            
        Returns:
            dict: 标签页信息
        """
        if not self.browser:
            await self.connect_or_open_browser()
            
        self.current_tab = self.browser.latest_tab
        self.current_tab.get(url)
        
        return {
            "title": self.current_tab.title,
            "tab_id": self.current_tab.tab_id,
            "url": self.current_tab.url
        }
    
    def wait(self, seconds: int) -> str:
        """等待指定秒数
        
        Args:
            seconds: 等待秒数
            
        Returns:
            str: 等待结果信息
        """
        if not self.browser:
            return "请先打开或连接浏览器"
            
        self.browser.latest_tab.wait(seconds)
        return f"等待{seconds}秒成功"
    
    def get_current_tab(self):
        """获取当前标签页
        
        Returns:
            ChromiumTab: 当前标签页对象
        """
        if self.browser:
            self.current_tab = self.browser.latest_tab
        return self.current_tab
    
    def get_browser_info(self) -> Dict[str, Any]:
        """获取浏览器信息
        
        Returns:
            dict: 浏览器信息
        """
        if not self.browser or not self.current_tab:
            return {"error": "浏览器未连接"}
            
        return {
            "browser_connected": True,
            "current_tab_title": self.current_tab.title,
            "current_tab_url": self.current_tab.url,
            "current_tab_id": self.current_tab.tab_id
        }
    
    def close_browser(self) -> str:
        """关闭浏览器
        
        Returns:
            str: 关闭结果信息
        """
        if self.browser:
            self.browser.quit()
            self.browser = None
            self.current_tab = None
            return "浏览器已关闭"
        return "浏览器未连接"