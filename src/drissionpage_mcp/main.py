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
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource, Prompt

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
from .config.settings import DEFAULT_CONFIG, INSTRUCTIONS, GLOBAL_PROMPT, get_config_value, get_env_config
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
        # 初始化FastMCP服务器
        self.app = FastMCP(
            name="DrissionPage MCP",
        )
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
        
        # 注册全局提示词
        self._register_global_prompt()
        
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
        async def click_element(selector: str, selector_type: str = "css", index: int = 0, 
                               smart_feedback: bool = True, use_cache: bool = True) -> str:
            """🎯 点击页面元素（智能优化版）
            
            ⚠️ 重要提示：使用此工具前，请务必遵循标准化工作流程：
            1. 📸 先使用 take_screenshot() 确认目标元素存在
            2. 🔍 使用 get_dom_tree() 或 find_elements() 分析页面结构
            3. 🎯 基于准确信息构建选择器，禁止猜测元素名称
            
            🎯 选择器优先级（推荐顺序）：
            - ID选择器：#element-id （最优先）
            - CSS类选择器：.class-name
            - 属性选择器：[data-testid="value"]
            - XPath选择器：//div[@class="example"]
            - 文本匹配：仅作为辅助手段

            Args:
                selector: 元素选择器（禁止猜测，必须基于实际DOM结构）
                selector_type: 选择器类型 (css, xpath, text)
                index: 元素索引（当有多个匹配时，从0开始）
                smart_feedback: 是否启用智能反馈（推荐True）
                use_cache: 是否使用缓存（推荐True以提升性能）

            Returns:
                str: 操作结果和反馈信息
                
            💡 最佳实践示例：
            - 正确：先 find_elements("button") 确认按钮存在，再 click_element("#submit-btn")
            - 错误：直接 click_element("#可能存在的按钮") 而不确认元素
            """
            try:
                if not self.element_handler:
                    return "请先连接浏览器"
                
                # 原因：使用统一的元素点击接口，支持更多选择器类型和智能反馈，副作用：无，回滚策略：还原原始逻辑
                return self.element_handler.click_element_unified(
                    selector, selector_type, index, smart_feedback, use_cache
                )
            except Exception as e:
                logger.error(f"点击元素失败: {e}")
                return f"点击元素失败: {str(e)}"
        
        @self.app.tool()
        async def input_text(selector: str, text: str, clear_first: bool = True) -> str:
            """⌨️ 在输入框中输入文本（智能优化版）
            
            ⚠️ 重要提示：使用此工具前，请务必遵循标准化工作流程：
            1. 📸 先使用 take_screenshot() 确认输入框存在且可见
            2. 🔍 使用 find_elements() 验证输入框的选择器
            3. 🎯 基于准确的DOM信息构建选择器
            
            🎯 输入框选择器优先级：
            - ID选择器：#input-id （最优先）
            - name属性：[name="username"]
            - CSS类选择器：.form-input
            - XPath选择器：//input[@type="text"]
            
            Args:
                selector: 输入框选择器（必须基于实际DOM结构，禁止猜测）
                text: 要输入的文本内容
                clear_first: 是否先清空输入框（推荐True避免内容叠加）
                
            Returns:
                str: 输入操作结果和反馈信息
                
            💡 最佳实践示例：
            - 正确：先 find_elements("input[type='text']") 确认输入框，再输入文本
            - 错误：直接对未确认的选择器输入文本
            """
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
            """📝 获取元素文本内容（精确定位版）
            
            ⚠️ 重要提示：这是预处理工具，用于获取精确的元素信息！
            使用场景：
            1. 🔍 在点击或输入操作前，验证目标元素的实际文本内容
            2. 📋 获取页面动态内容，如表格数据、状态信息等
            3. ✅ 确认元素存在性和可见性
            
            🎯 选择器构建原则：
            - 必须基于 get_dom_tree() 或 find_elements() 的结果
            - 禁止猜测元素选择器
            - 优先使用ID、class、属性选择器
            
            Args:
                selector: 元素选择器（必须基于实际DOM结构）
                
            Returns:
                str: 元素的文本内容，如果元素不存在则返回错误信息
                
            💡 最佳实践示例：
            - 正确：先 find_elements(".status") 确认元素，再 get_element_text(".status")
            - 错误：直接 get_element_text("#可能的状态元素") 而不确认
            """
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
            """📄 获取页面完整文本内容（预处理必备工具）
            
            ⚠️ 核心预处理工具：这是标准化工作流程的第2步！
            
            🔧 主要用途：
            1. 🔍 在操作元素前，获取页面的完整文本信息
            2. 📋 为非多模态LLM提供详细的页面内容描述
            3. 🎯 帮助构建精确的元素选择器
            4. ✅ 确认页面加载完成和内容可用性
            
            💡 与其他工具的配合使用：
            - 配合 take_screenshot()：视觉+文本双重确认
            - 配合 get_dom_tree()：结构化分析页面布局
            - 配合 find_elements()：基于文本内容定位元素
            
            Returns:
                str: 页面的完整可见文本内容（去除HTML标签）
                
            🚀 推荐工作流程：
            1. take_screenshot() - 获取页面截图
            2. get_page_text() - 获取页面文本（当前步骤）
            3. get_dom_tree() - 分析页面结构
            4. 基于以上信息执行具体操作
            """
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
            """📸 截取页面截图（标准化工作流程第1步）
            
            ⚠️ 核心预处理工具：这是标准化工作流程的第1步！
            
            🎯 主要用途：
            1. 🔍 视觉确认：在任何元素操作前，先确认目标元素存在
            2. 📋 为多模态LLM提供视觉上下文信息
            3. 🐛 调试辅助：操作失败时用于问题诊断
            4. 📝 文档记录：保存操作过程的视觉证据
            
            💡 与其他工具的配合：
            - 多模态LLM：截图 → 视觉分析 → 精确操作
            - 非多模态LLM：截图 → get_page_text() → get_dom_tree() → 操作
            
            Args:
                filename: 截图文件名（可选，自动生成时间戳命名）
                full_page: 是否截取完整页面（True）还是可视区域（False）
                element_selector: 仅截取特定元素（可选）
                
            Returns:
                str: 截图保存路径和操作结果
                
            🚀 推荐使用场景：
            - 每次页面导航后立即截图确认加载状态
            - 点击、输入等操作前截图确认目标元素
            - 操作失败时截图辅助问题诊断
            """
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
            """🌳 获取DOM树结构（结构化分析工具）
            
            ⚠️ 核心分析工具：这是标准化工作流程的第3步！
            
            🎯 主要用途：
            1. 📋 获取页面的层次化结构信息
            2. 🔍 为元素定位提供精确的选择器路径
            3. 🎯 分析页面布局，理解元素间的父子关系
            4. 🛠️ 为非多模态LLM提供详细的结构化信息
            
            💡 与其他工具的协作：
            - 在 take_screenshot() 和 get_page_text() 之后使用
            - 为 find_elements() 提供选择器构建依据
            - 配合 get_element_text() 验证元素内容
            
            Args:
                selector: 起始选择器（默认"body"获取整个页面结构）
                max_depth: 最大遍历深度（默认10层，避免过深嵌套）
                
            Returns:
                str: 结构化的DOM树信息，包含标签、属性、层级关系
                
            🚀 使用建议：
            - 首次分析页面：使用默认参数获取完整结构
            - 聚焦特定区域：指定具体的selector缩小范围
            - 复杂页面：适当减少max_depth避免信息过载
            """
            try:
                if not self.dom_service:
                    return "请先连接浏览器"
                
                # 原因：修复max_depth参数传递，确保深度控制功能正常工作，副作用：无，回滚策略：移除max_depth参数
                if selector == "body":
                    return str(self.dom_service.get_simplified_dom_tree(max_depth))
                else:
                    return str(self.dom_service.get_dom_tree_by_selector(selector, max_depth))
            except Exception as e:
                logger.error(f"获取DOM树失败: {e}")
                return f"获取DOM树失败: {str(e)}"
        
        @self.app.tool()
        async def find_elements(selector: str, selector_type: str = "css", 
                               limit: int = 10, include_similar: bool = True) -> str:
            """🔍 查找页面元素（智能定位工具）
            
            ⚠️ 精确定位工具：基于DOM分析结果进行元素查找！
            
            🎯 主要用途：
            1. 🔍 基于get_dom_tree()结果，精确定位目标元素
            2. 📋 验证元素存在性和可访问性
            3. 🎯 获取元素的详细属性信息（id、class、text等）
            4. 🛠️ 为后续操作提供准确的选择器
            
            💡 选择器类型优先级：
            1. CSS选择器：#id、.class、[attribute]（推荐）
            2. XPath：//div[@class='example']（复杂定位）
            3. 文本匹配："按钮文字"（辅助手段）
            
            Args:
                selector: 元素选择器（必须基于实际DOM结构）
                selector_type: 选择器类型（css/xpath/text）
                limit: 返回元素数量限制（避免结果过多）
                include_similar: 是否包含相似元素（智能匹配）
                
            Returns:
                str: 匹配元素的详细信息列表
                
            🚀 最佳实践：
            - 先用get_dom_tree()分析页面结构
            - 基于结构信息构建精确选择器
            - 验证找到的元素是否为目标元素
            - 将结果用于click_element()或input_text()操作
                
            Returns:
                str: 查找结果
            """
            # 原因：添加limit和include_similar参数支持，使用统一的元素查找接口，副作用：无，回滚策略：还原原始逻辑
            try:
                if not self.element_handler:
                    return "请先连接浏览器"
                
                # 使用统一的元素查找接口
                elements = self.element_handler.find_elements_unified(
                    selector, selector_type, limit, include_similar
                )
                
                if not elements:
                    return "未找到匹配的元素"
                
                # 如果有错误，直接返回
                if len(elements) == 1 and "error" in elements[0]:
                    return str(elements[0]["error"])
                
                return str(elements)
            except Exception as e:
                logger.error(f"查找元素失败: {e}")
                return f"查找元素失败: {str(e)}"
        
        # 网络监控工具
        @self.app.tool()
        async def enable_network_monitoring(filter_types: List[str] = None) -> str:
            """启用网络监控
            
            Args:
                filter_types: 需要监听的mimeType类型列表
                
            Returns:
                str: 启用结果
            """
            # 原因：支持List[str]类型的多过滤器，使用新的多过滤器监听接口，副作用：无，回滚策略：还原单一过滤器逻辑
            try:
                if not self.network_listener:
                    return "请先连接浏览器"
                
                # 使用多过滤器监听接口
                if filter_types:
                    return self.network_listener.setup_multi_filter_listener(filter_types)
                else:
                    return self.network_listener.enable_network_domain()
            except Exception as e:
                logger.error(f"启用网络监控失败: {e}")
                return f"启用网络监控失败: {str(e)}"
        
        @self.app.tool()
        async def get_network_logs(limit: int = 50) -> str:
            """获取网络请求日志
            
            Args:
                limit: 返回日志的最大数量
                
            Returns:
                str: 网络日志数据
            """
            # 原因：使用新的限制数量接口，简化逻辑并提供更好的性能，副作用：无，回滚策略：还原原始逻辑
            try:
                if not self.network_listener:
                    return "请先连接浏览器"
                
                # 使用新的限制数量接口
                limited_data = self.network_listener.get_response_listener_data_limited(limit)
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
    
    def _register_global_prompt(self):
        """注册全局提示词"""
        
        @self.app.prompt(name="global_automation_hints")
        async def global_automation_hints() -> Prompt:
            """永远附加的全局自动化测试操作提示"""
            return Prompt(
                name="global_automation_hints",
                description="DrissionPage MCP 自动化测试最佳实践全局提示",
                messages=[
                    {
                        "role": "system",
                        "content": GLOBAL_PROMPT
                    }
                ]
            )
    
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
        # 原因：修复新标签页切换bug，传入browser_manager以支持标签页自动切换，副作用：无，回滚策略：移除browser_manager参数
        self.element_handler = ElementHandler(tab, self.browser_manager)
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