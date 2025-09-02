# -*- coding: utf-8 -*-
"""网络监听模块

负责CDP事件监听和网络数据包监听功能。
"""

from typing import Dict, Any, List, Literal, Callable
from DrissionPage import Chromium


class NetworkListener:
    """网络监听器
    
    负责CDP事件监听和网络响应监听。
    """
    
    def __init__(self, tab):
        self.tab = tab
        self.cdp_event_data: List[Dict[str, Any]] = []
        self.response_listener_data: List[Dict[str, Any]] = []
    
    def run_cdp(self, cmd: str, **cmd_args) -> Any:
        """在当前标签页中运行谷歌CDP协议代码并获取结果
        
        Args:
            cmd: CDP协议命令
            **cmd_args: CDP命令参数
            
        Returns:
            Any: CDP命令执行结果
            
        Examples:
            run_cdp('Page.stopLoading')
            run_cdp('Page.navigate', url='https://example.com')
        """
        result = self.tab.run_cdp(cmd, **cmd_args)
        return result
    
    def listen_cdp_event(self, event_name: str) -> str:
        """设置监听CDP事件
        
        Args:
            event_name: CDP事件名称
            
        Returns:
            str: 设置结果
            
        Note:
            应该先运行CDP命令激活对应的域，比如 Network.enable
        """
        def callback(**event):
            self.cdp_event_data.append({
                "event_name": event_name, 
                "event_data": event
            })

        try:
            self.tab.driver.set_callback(event_name, callback)
            return f"CDP event callback for '{event_name}' set successfully."
        except Exception as e:
            return f"设置CDP事件监听失败: {str(e)}"
    
    def get_cdp_event_data(self) -> List[Dict[str, Any]]:
        """获取CDP事件回调函数收集到的数据
        
        Returns:
            list: CDP事件数据列表
        """
        return self.cdp_event_data
    
    def clear_cdp_event_data(self) -> str:
        """清空CDP事件数据
        
        Returns:
            str: 清空结果
        """
        self.cdp_event_data.clear()
        return "CDP事件数据已清空"
    
    def setup_response_listener(
        self,
        mime_type: Literal[
            # 文本类
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript",
            "text/plain",
            "text/xml",
            "text/csv",
            "application/json",
            
            # 应用类
            "application/octet-stream",
            "application/zip",
            "application/pdf",    
            "multipart/form-data",
            "application/xml",
            
            # 图片类
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            "image/x-icon",
            
            # 音视频类
            "audio/mpeg",
            "audio/ogg",
            "video/mp4",
            "video/webm",
            "video/ogg"
        ],
        url_include: str = "."
    ) -> str:
        """设置网络响应监听
        
        Args:
            mime_type: 需要监听的接收的数据包的mimeType类型
            url_include: 需要监听的接收的数据包的url包含的关键字
            
        Returns:
            str: 设置结果
        """
        # 启用网络域
        self.tab.run_cdp("Network.enable")

        def response_callback(**event):
            response = event.get("response", {})
            _url = response.get("url", "")
            _mime_type = response.get("mimeType", "")
            
            if mime_type in _mime_type and url_include in _url:
                self.response_listener_data.append({
                    "event_name": "Network.responseReceived",
                    "event_data": event
                })
        
        try:
            self.tab.driver.set_callback("Network.responseReceived", response_callback)
            return f"网络响应监听设置成功，监听mimeType: {mime_type}, URL包含: {url_include}"
        except Exception as e:
            return f"设置网络响应监听失败: {str(e)}"
    
    def setup_multi_filter_listener(self, filter_types: List[str] = None, url_include: str = ".") -> str:
        """设置多过滤器网络响应监听
        
        Args:
            filter_types: 需要监听的mimeType类型列表
            url_include: 需要监听的url包含的关键字
            
        Returns:
            str: 设置结果
        """
        # 原因：支持List[str]类型的多过滤器，提升网络监听的灵活性，副作用：无，回滚策略：移除此方法
        if not filter_types:
            filter_types = ["application/json"]
        
        # 启用网络域
        self.tab.run_cdp("Network.enable")

        def multi_response_callback(**event):
            response = event.get("response", {})
            _url = response.get("url", "")
            _mime_type = response.get("mimeType", "")
            
            # 检查是否匹配任一过滤器类型
            type_matched = any(filter_type in _mime_type for filter_type in filter_types)
            
            if type_matched and url_include in _url:
                self.response_listener_data.append({
                    "event_name": "Network.responseReceived",
                    "event_data": event,
                    "matched_filters": [ft for ft in filter_types if ft in _mime_type]
                })
        
        try:
            self.tab.driver.set_callback("Network.responseReceived", multi_response_callback)
            return f"多过滤器网络响应监听设置成功，监听类型: {filter_types}, URL包含: {url_include}"
        except Exception as e:
            return f"设置多过滤器网络响应监听失败: {str(e)}"
    
    def stop_response_listener(self, clear_data: bool = False) -> str:
        """关闭监听网页发送的数据包
        
        Args:
            clear_data: 是否清空已收集的数据
            
        Returns:
            str: 关闭结果
        """
        try:
            self.tab.run_cdp("Network.disable")
            if clear_data:
                self.response_listener_data.clear()
            return f"网络响应监听关闭成功，是否清空数据: {clear_data}"
        except Exception as e:
            return f"关闭网络响应监听失败: {str(e)}"
    
    def get_response_listener_data(self) -> List[Dict[str, Any]]:
        """获取网络响应监听收集到的数据
        
        Returns:
            list: 网络响应数据列表
        """
        return self.response_listener_data
    
    def get_response_listener_data_limited(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取限制数量的网络响应监听数据
        
        Args:
            limit: 返回数据的最大数量
            
        Returns:
            list: 限制数量的网络响应数据列表
        """
        # 原因：添加limit参数支持，提供数据量控制功能，副作用：无，回滚策略：移除此方法
        if limit <= 0:
            return []
        return self.response_listener_data[-limit:] if len(self.response_listener_data) > limit else self.response_listener_data
    
    def clear_response_listener_data(self) -> str:
        """清空网络响应监听数据
        
        Returns:
            str: 清空结果
        """
        self.response_listener_data.clear()
        return "网络响应监听数据已清空"
    
    def get_network_stats(self) -> Dict[str, Any]:
        """获取网络监听统计信息
        
        Returns:
            dict: 统计信息
        """
        return {
            "cdp_events_count": len(self.cdp_event_data),
            "response_events_count": len(self.response_listener_data),
            "latest_cdp_event": self.cdp_event_data[-1] if self.cdp_event_data else None,
            "latest_response_event": self.response_listener_data[-1] if self.response_listener_data else None
        }
    
    def enable_network_domain(self) -> str:
        """启用网络域
        
        Returns:
            str: 启用结果
        """
        try:
            self.tab.run_cdp("Network.enable")
            return "网络域启用成功"
        except Exception as e:
            return f"启用网络域失败: {str(e)}"
    
    def disable_network_domain(self) -> str:
        """禁用网络域
        
        Returns:
            str: 禁用结果
        """
        try:
            self.tab.run_cdp("Network.disable")
            return "网络域禁用成功"
        except Exception as e:
            return f"禁用网络域失败: {str(e)}"
    
    def clear_browser_cache(self) -> str:
        """清空浏览器缓存
        
        Returns:
            str: 清空结果
        """
        try:
            self.tab.run_cdp("Network.clearBrowserCache")
            return "浏览器缓存清空成功"
        except Exception as e:
            return f"清空浏览器缓存失败: {str(e)}"
    
    def set_user_agent(self, user_agent: str) -> str:
        """设置用户代理
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            str: 设置结果
        """
        try:
            self.tab.run_cdp("Network.setUserAgentOverride", userAgent=user_agent)
            return f"用户代理设置成功: {user_agent}"
        except Exception as e:
            return f"设置用户代理失败: {str(e)}"