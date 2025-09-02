# -*- coding: utf-8 -*-
"""CDP服务模块

负责Chrome DevTools Protocol相关功能。
"""

from typing import Dict, Any, List, Optional, Callable
from DrissionPage import Chromium


class CDPService:
    """CDP服务
    
    负责Chrome DevTools Protocol的各种操作。
    """
    
    def __init__(self, tab):
        self.tab = tab
        self.event_listeners: Dict[str, List[Callable]] = {}
        self.collected_events: Dict[str, List[Dict[str, Any]]] = {}
    
    def run_command(self, command: str, **params) -> Any:
        """执行CDP命令
        
        Args:
            command: CDP命令名称
            **params: 命令参数
            
        Returns:
            Any: 命令执行结果
        """
        try:
            result = self.tab.run_cdp(command, **params)
            return result
        except Exception as e:
            return {"error": f"CDP命令执行失败: {str(e)}"}
    
    def enable_domain(self, domain: str) -> str:
        """启用CDP域
        
        Args:
            domain: 域名称（如 Network, Runtime, Page等）
            
        Returns:
            str: 启用结果
        """
        try:
            self.run_command(f"{domain}.enable")
            return f"{domain} 域启用成功"
        except Exception as e:
            return f"启用 {domain} 域失败: {str(e)}"
    
    def disable_domain(self, domain: str) -> str:
        """禁用CDP域
        
        Args:
            domain: 域名称
            
        Returns:
            str: 禁用结果
        """
        try:
            self.run_command(f"{domain}.disable")
            return f"{domain} 域禁用成功"
        except Exception as e:
            return f"禁用 {domain} 域失败: {str(e)}"
    
    def add_event_listener(self, event_name: str, callback: Optional[Callable] = None) -> str:
        """添加事件监听器
        
        Args:
            event_name: 事件名称
            callback: 回调函数，如果不提供则使用默认收集器
            
        Returns:
            str: 添加结果
        """
        try:
            if callback is None:
                # 使用默认收集器
                def default_callback(**event_data):
                    if event_name not in self.collected_events:
                        self.collected_events[event_name] = []
                    self.collected_events[event_name].append({
                        "timestamp": event_data.get("timestamp", ""),
                        "data": event_data
                    })
                callback = default_callback
            
            # 注册回调
            self.tab.driver.set_callback(event_name, callback)
            
            # 记录监听器
            if event_name not in self.event_listeners:
                self.event_listeners[event_name] = []
            self.event_listeners[event_name].append(callback)
            
            return f"事件监听器 {event_name} 添加成功"
        except Exception as e:
            return f"添加事件监听器失败: {str(e)}"
    
    def get_collected_events(self, event_name: Optional[str] = None) -> Dict[str, Any]:
        """获取收集到的事件数据
        
        Args:
            event_name: 事件名称，如果不指定则返回所有事件
            
        Returns:
            dict: 事件数据
        """
        if event_name:
            return {
                event_name: self.collected_events.get(event_name, [])
            }
        return self.collected_events
    
    def clear_collected_events(self, event_name: Optional[str] = None) -> str:
        """清空收集到的事件数据
        
        Args:
            event_name: 事件名称，如果不指定则清空所有事件
            
        Returns:
            str: 清空结果
        """
        if event_name:
            if event_name in self.collected_events:
                del self.collected_events[event_name]
                return f"事件 {event_name} 的数据已清空"
            else:
                return f"事件 {event_name} 不存在"
        else:
            self.collected_events.clear()
            return "所有事件数据已清空"
    
    def get_event_stats(self) -> Dict[str, Any]:
        """获取事件统计信息
        
        Returns:
            dict: 统计信息
        """
        stats = {
            "total_events": len(self.collected_events),
            "event_counts": {},
            "active_listeners": list(self.event_listeners.keys())
        }
        
        for event_name, events in self.collected_events.items():
            stats["event_counts"][event_name] = len(events)
        
        return stats
    
    # Network 域相关方法
    def enable_network_monitoring(self) -> str:
        """启用网络监控
        
        Returns:
            str: 启用结果
        """
        result = self.enable_domain("Network")
        
        # 添加常用网络事件监听
        self.add_event_listener("Network.requestWillBeSent")
        self.add_event_listener("Network.responseReceived")
        self.add_event_listener("Network.loadingFinished")
        self.add_event_listener("Network.loadingFailed")
        
        return result + " - 网络事件监听已启用"
    
    def disable_network_monitoring(self) -> str:
        """禁用网络监控
        
        Returns:
            str: 禁用结果
        """
        return self.disable_domain("Network")
    
    def clear_browser_cache(self) -> str:
        """清空浏览器缓存
        
        Returns:
            str: 清空结果
        """
        try:
            self.run_command("Network.clearBrowserCache")
            return "浏览器缓存已清空"
        except Exception as e:
            return f"清空浏览器缓存失败: {str(e)}"
    
    def set_user_agent_override(self, user_agent: str) -> str:
        """设置用户代理覆盖
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            str: 设置结果
        """
        try:
            self.run_command("Network.setUserAgentOverride", userAgent=user_agent)
            return f"用户代理已设置: {user_agent}"
        except Exception as e:
            return f"设置用户代理失败: {str(e)}"
    
    def set_cache_disabled(self, disabled: bool = True) -> str:
        """设置缓存禁用状态
        
        Args:
            disabled: 是否禁用缓存
            
        Returns:
            str: 设置结果
        """
        try:
            self.run_command("Network.setCacheDisabled", cacheDisabled=disabled)
            status = "禁用" if disabled else "启用"
            return f"缓存已{status}"
        except Exception as e:
            return f"设置缓存状态失败: {str(e)}"
    
    # Runtime 域相关方法
    def enable_runtime_monitoring(self) -> str:
        """启用运行时监控
        
        Returns:
            str: 启用结果
        """
        result = self.enable_domain("Runtime")
        
        # 添加运行时事件监听
        self.add_event_listener("Runtime.consoleAPICalled")
        self.add_event_listener("Runtime.exceptionThrown")
        
        return result + " - 运行时事件监听已启用"
    
    def evaluate_expression(self, expression: str) -> Any:
        """执行JavaScript表达式
        
        Args:
            expression: JavaScript表达式
            
        Returns:
            Any: 执行结果
        """
        try:
            result = self.run_command("Runtime.evaluate", expression=expression)
            return result
        except Exception as e:
            return {"error": f"执行JavaScript失败: {str(e)}"}
    
    # Page 域相关方法
    def enable_page_monitoring(self) -> str:
        """启用页面监控
        
        Returns:
            str: 启用结果
        """
        result = self.enable_domain("Page")
        
        # 添加页面事件监听
        self.add_event_listener("Page.loadEventFired")
        self.add_event_listener("Page.domContentEventFired")
        self.add_event_listener("Page.frameNavigated")
        
        return result + " - 页面事件监听已启用"
    
    def navigate_to_url(self, url: str) -> str:
        """导航到指定URL
        
        Args:
            url: 目标URL
            
        Returns:
            str: 导航结果
        """
        try:
            self.run_command("Page.navigate", url=url)
            return f"已导航到: {url}"
        except Exception as e:
            return f"导航失败: {str(e)}"
    
    def reload_page(self, ignore_cache: bool = False) -> str:
        """重新加载页面
        
        Args:
            ignore_cache: 是否忽略缓存
            
        Returns:
            str: 重载结果
        """
        try:
            self.run_command("Page.reload", ignoreCache=ignore_cache)
            cache_status = "忽略缓存" if ignore_cache else "使用缓存"
            return f"页面已重新加载 ({cache_status})"
        except Exception as e:
            return f"重新加载页面失败: {str(e)}"
    
    def stop_loading(self) -> str:
        """停止页面加载
        
        Returns:
            str: 停止结果
        """
        try:
            self.run_command("Page.stopLoading")
            return "页面加载已停止"
        except Exception as e:
            return f"停止页面加载失败: {str(e)}"
    
    # Security 域相关方法
    def enable_security_monitoring(self) -> str:
        """启用安全监控
        
        Returns:
            str: 启用结果
        """
        result = self.enable_domain("Security")
        
        # 添加安全事件监听
        self.add_event_listener("Security.securityStateChanged")
        
        return result + " - 安全事件监听已启用"
    
    def set_ignore_certificate_errors(self, ignore: bool = True) -> str:
        """设置是否忽略证书错误
        
        Args:
            ignore: 是否忽略证书错误
            
        Returns:
            str: 设置结果
        """
        try:
            self.run_command("Security.setIgnoreCertificateErrors", ignore=ignore)
            status = "忽略" if ignore else "不忽略"
            return f"证书错误设置为{status}"
        except Exception as e:
            return f"设置证书错误处理失败: {str(e)}"
    
    def get_domain_status(self) -> Dict[str, bool]:
        """获取各域的启用状态
        
        Returns:
            dict: 域状态信息
        """
        domains = ["Network", "Runtime", "Page", "Security", "DOM", "CSS"]
        status = {}
        
        for domain in domains:
            try:
                # 尝试获取域信息来判断是否启用
                result = self.run_command(f"{domain}.enable")
                status[domain] = not isinstance(result, dict) or "error" not in result
            except:
                status[domain] = False
        
        return status