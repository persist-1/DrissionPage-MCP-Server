# -*- coding: utf-8 -*-
"""DrissionPage MCP 主入口模块

整合所有功能组件，提供统一的MCP服务接口。
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# FastMCP 框架
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

# 核心模块
from .core.browser_manager import BrowserManager
from .core.element_handler import ElementHandler
from .core.network_listener import NetworkListener
from .core.file_handler import FileHandler

# 服务模块
from .services.dom_service import DOMService
from .services.screenshot_service import ScreenshotService
from .services.cdp_service import CDPService

# 配置和工具
from .config.settings import DEFAULT_CONFIG, INSTRUCTIONS, get_config_value, get_env_config
from .utils.helpers import (
    get_dom_tree_json, save_dict_to_sqlite, ensure_directory,
    format_timestamp, safe_filename, validate_url
)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DrissionPageMCP:
    """DrissionPage MCP 主服务类
    
    整合所有功能模块，提供统一的MCP服务接口。
    """
    
    def __init__(self):
        self.app = FastMCP("DrissionPage MCP")
        self.browser_manager = None
        self.element_handler = None
        self.network_listener = None
        self.file_handler = None
        self.dom_service = None
        self.screenshot_service = None
        self.cdp_service = None
        
        # 初始化配置
        self.config = DEFAULT_CONFIG.copy()
        self.config.update(get_env_config())
        
        # 注册所有工具
        self._register_tools()
        
        # 注册资源
        self._register_resources()
    
    def _register_tools(self):
        """注册所有MCP工具"""
        
        # 浏览器管理工具
        @self.app.tool()
        async def connect_browser(port: int = 9222, headless: bool = False, user_data_dir: str = None) -> str:
            """连接到浏览器或启动新浏览器"""
            try:
                if not self.browser_manager:
                    self.browser_manager = BrowserManager()
                
                config = {
                    "debug_port": port,
                    "headless": headless
                }
                if user_data_dir:
                    config["user_data_dir"] = user_data_dir
                    
                # 修复：connect_or_open_browser不是异步方法
                result = self.browser_manager.connect_or_open_browser(config)
                
                # 初始化其他服务
                if self.browser_manager.current_tab:
                    self._initialize_services()
                
                return f"浏览器连接成功: {result['latest_tab_title']} - {result['browser_address']}"
            except Exception as e:
                logger.error(f"连接浏览器失败: {e}")
                return f"连接浏览器失败: {str(e)}"
        
        @self.app.tool()
        async def new_tab(url: str = None) -> str:
            """创建新标签页"""
            try:
                if not self.browser_manager:
                    return "请先连接浏览器"
                
                result = await self.browser_manager.new_tab(url)
                
                # 重新初始化服务
                if self.browser_manager.current_tab:
                    self._initialize_services()
                
                return f"新标签页创建成功: {result['title']} - {result['url']}"
            except Exception as e:
                logger.error(f"创建标签页失败: {e}")
                return f"创建标签页失败: {str(e)}"
        
        @self.app.tool()
        async def navigate(url: str) -> str:
            """导航到指定URL"""
            try:
                if not self.browser_manager:
                    return "请先连接浏览器"
                
                if not validate_url(url):
                    return f"无效的URL: {url}"
                
                result = await self.browser_manager.get(url)
                return f"导航成功: {result['title']} - {result['url']}"
            except Exception as e:
                logger.error(f"导航失败: {e}")
                return f"导航失败: {str(e)}"
        
        # 元素操作工具
        @self.app.tool()
        async def click_element(selector: str, selector_type: str = "css", index: int = 0) -> str:
            """点击页面元素"""
            try:
                if not self.element_handler:
                    return "请先连接浏览器"
                
                if selector_type == "xpath":
                    # 修复：click_by_xpath不是异步方法
                    result = self.element_handler.click_by_xpath(selector)
                    return str(result)
                elif selector_type == "text":
                    # 修复：click_by_containing_text不是异步方法
                    return self.element_handler.click_by_containing_text(selector, index)
                else:
                    # CSS选择器
                    element = self.element_handler.tab.ele(selector, index=index + 1)
                    if element:
                        element.click()
                        return f"成功点击元素: {selector}"
                    else:
                        return f"未找到元素: {selector}"
            except Exception as e:
                logger.error(f"点击元素失败: {e}")
                return f"点击元素失败: {str(e)}"
        
        @self.app.tool()
        async def input_text(selector: str, text: str, clear_first: bool = True) -> str:
            """在输入框中输入文本"""
            try:
                if not self.element_handler:
                    return "请先连接浏览器"
                
                # 修复：input_by_xpath不是异步方法
                result = self.element_handler.input_by_xpath(selector, text, clear_first)
                return str(result)
            except Exception as e:
                logger.error(f"输入文本失败: {e}")
                return f"输入文本失败: {str(e)}"
        
        @self.app.tool()
        async def get_element_text(selector: str) -> str:
            """获取元素文本内容"""
            try:
                if not self.element_handler:
                    return "请先连接浏览器"
                
                element = self.element_handler.tab.ele(selector)
                if element:
                    return element.text or ""
                else:
                    return f"未找到元素: {selector}"
            except Exception as e:
                logger.error(f"获取元素文本失败: {e}")
                return f"获取元素文本失败: {str(e)}"
        
        @self.app.tool()
        async def get_page_text() -> str:
            """获取页面文本内容"""
            try:
                if not self.element_handler:
                    return "请先连接浏览器"
                
                # 修复：get_body_text不是异步方法
                return self.element_handler.get_body_text()
            except Exception as e:
                logger.error(f"获取页面文本失败: {e}")
                return f"获取页面文本失败: {str(e)}"
        
        # 截图工具
        @self.app.tool()
        async def take_screenshot(filename: str = None, full_page: bool = False, element_selector: str = None) -> str:
            """截取页面截图"""
            try:
                if not self.screenshot_service:
                    return "请先连接浏览器"
                
                # 使用新的目录结构，传入None让服务自动处理路径
                if element_selector:
                    return self.screenshot_service.capture_element(element_selector, None, filename)
                elif full_page:
                    return self.screenshot_service.capture_full_page(None, filename)
                else:
                    return self.screenshot_service.capture_viewport(None, filename)
            except Exception as e:
                logger.error(f"截图失败: {e}")
                return f"截图失败: {str(e)}"
        
        @self.app.tool()
        async def get_screenshot_data(format: str = "png") -> bytes:
            """获取截图二进制数据"""
            try:
                if not self.screenshot_service:
                    raise Exception("请先连接浏览器")
                
                # 修复：使用正确的方法名，且不是异步方法
                return self.screenshot_service.get_screenshot_bytes(format)
            except Exception as e:
                logger.error(f"获取截图数据失败: {e}")
                raise Exception(f"获取截图数据失败: {str(e)}")
        
        # DOM操作工具
        @self.app.tool()
        async def get_dom_tree(selector: str = "body", max_depth: int = 10) -> str:
            """获取DOM树结构"""
            try:
                if not self.dom_service:
                    return "请先连接浏览器"
                
                # 修复：根据selector参数选择合适的方法
                if selector == "body":
                    return str(self.dom_service.get_simplified_dom_tree())
                else:
                    return str(self.dom_service.get_dom_tree_by_selector(selector))
            except Exception as e:
                logger.error(f"获取DOM树失败: {e}")
                return f"获取DOM树失败: {str(e)}"
        
        @self.app.tool()
        async def find_elements(selector: str, selector_type: str = "css") -> str:
            """查找页面元素"""
            try:
                if not self.dom_service:
                    return "请先连接浏览器"
                
                if selector_type == "text":
                    # 修复：使用正确的方法名 search_elements_by_text
                    elements = self.dom_service.search_elements_by_text(selector)
                    return str(elements)
                else:
                    # 修复：使用正确的方法名，且不是异步方法
                    return str(self.dom_service.get_element_info(selector))
            except Exception as e:
                logger.error(f"查找元素失败: {e}")
                return f"查找元素失败: {str(e)}"
        
        # 网络监控工具
        @self.app.tool()
        async def enable_network_monitoring(filter_types: List[str] = None) -> str:
            """启用网络监控"""
            try:
                if not self.network_listener:
                    return "请先连接浏览器"
                
                # 修复：network_listener的方法都是同步的，且使用正确的方法名
                if filter_types:
                    return self.network_listener.setup_response_listener(filter_types[0] if filter_types else "application/json")
                else:
                    return self.network_listener.enable_network_domain()
            except Exception as e:
                logger.error(f"启用网络监控失败: {e}")
                return f"启用网络监控失败: {str(e)}"
        
        @self.app.tool()
        async def get_network_logs(limit: int = 50) -> str:
            """获取网络请求日志"""
            try:
                if not self.network_listener:
                    return "请先连接浏览器"
                
                # 修复：get_response_listener_data不是异步方法，且不接受limit参数
                data = self.network_listener.get_response_listener_data()
                # 限制返回的数据量
                limited_data = data[-limit:] if len(data) > limit else data
                return str(limited_data)
            except Exception as e:
                logger.error(f"获取网络日志失败: {e}")
                return f"获取网络日志失败: {str(e)}"
        
        # 文件操作工具
        @self.app.tool()
        async def save_page_source(filename: str = None) -> str:
            """保存页面源码到文件"""
            try:
                if not self.file_handler:
                    return "请先连接浏览器"
                
                # 修复：file_handler.save_page_source不是异步方法
                return self.file_handler.save_page_source(filename)
            except Exception as e:
                logger.error(f"保存页面源码失败: {e}")
                return f"保存页面源码失败: {str(e)}"
        
        @self.app.tool()
        async def get_cookies() -> str:
            """获取当前页面的Cookies"""
            try:
                if not self.browser_manager or not self.browser_manager.current_tab:
                    return "请先连接浏览器"
                
                # 修复：直接从tab获取cookies，file_handler没有get_cookies方法
                cookies = self.browser_manager.current_tab.cookies()
                return str(cookies)
            except Exception as e:
                logger.error(f"获取Cookies失败: {e}")
                return f"获取Cookies失败: {str(e)}"
        
        # JavaScript执行工具
        @self.app.tool()
        async def execute_javascript(code: str, return_result: bool = True) -> str:
            """执行JavaScript代码"""
            try:
                if not self.element_handler:
                    return "请先连接浏览器"
                
                # 修复：直接调用tab的run_js方法，不是异步方法
                return self.element_handler.tab.run_js(code)
            except Exception as e:
                logger.error(f"执行JavaScript失败: {e}")
                return f"执行JavaScript失败: {str(e)}"
        
        # CDP命令工具
        @self.app.tool()
        async def run_cdp_command(command: str, **params) -> str:
            """执行CDP命令"""
            try:
                if not self.cdp_service:
                    return "请先连接浏览器"
                
                result = self.cdp_service.run_command(command, **params)
                return str(result)
            except Exception as e:
                logger.error(f"执行CDP命令失败: {e}")
                return f"执行CDP命令失败: {str(e)}"
    
    def _register_resources(self):
        """注册MCP资源"""
        
        @self.app.resource("config://default")
        async def get_default_config() -> str:
            """获取默认配置"""
            import json
            return json.dumps(self.config, indent=2, ensure_ascii=False)
        
        @self.app.resource("instructions://all")
        async def get_all_instructions() -> str:
            """获取所有工具指令"""
            import json
            return json.dumps(INSTRUCTIONS, indent=2, ensure_ascii=False)
        
        @self.app.resource("status://browser")
        async def get_browser_status() -> str:
            """获取浏览器状态"""
            if not self.browser_manager:
                return "浏览器未连接"
            
            status = {
                "connected": self.browser_manager.browser is not None,
                "current_tab": self.browser_manager.current_tab is not None,
                "tab_count": len(self.browser_manager.browser.tabs) if self.browser_manager.browser else 0
            }
            
            if self.browser_manager.current_tab:
                try:
                    status["current_url"] = self.browser_manager.current_tab.url
                    status["title"] = self.browser_manager.current_tab.title
                except:
                    pass
            
            import json
            return json.dumps(status, indent=2, ensure_ascii=False)
    
    def _initialize_services(self):
        """初始化所有服务模块"""
        if not self.browser_manager or not self.browser_manager.current_tab:
            return
        
        tab = self.browser_manager.current_tab
        
        # 初始化核心服务
        self.element_handler = ElementHandler(tab)
        self.network_listener = NetworkListener(tab)
        self.file_handler = FileHandler(tab)
        
        # 初始化业务服务
        self.dom_service = DOMService(tab)
        self.screenshot_service = ScreenshotService(tab)
        self.cdp_service = CDPService(tab)
        
        logger.info("所有服务模块初始化完成")
    
    def run(self):
        """运行MCP服务器"""
        try:
            logger.info("启动DrissionPage MCP服务器 (STDIO模式)")

            self.app.run()
        except KeyboardInterrupt:
            logger.info("服务器已停止")
        except Exception as e:
            logger.error(f"服务器运行错误: {e}")


def main():
    """主入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DrissionPage MCP Server")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    # 创建并运行服务器
    server = DrissionPageMCP()
    server.run()


if __name__ == "__main__":
    main()