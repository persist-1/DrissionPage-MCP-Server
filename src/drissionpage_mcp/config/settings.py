# -*- coding: utf-8 -*-
"""配置管理模块

定义默认配置和系统设置。
"""

from typing import Dict, Any, List
import os
from pathlib import Path


# 全局提示词配置
GLOBAL_PROMPT = """
🔧 DrissionPage MCP 自动化测试最佳实践指南

⚠️ 重要提示：在进行任何元素操作前，请严格遵循以下工作流程：

📋 标准化工作流程：
1. 📸 视觉确认：使用 take_screenshot() 获取页面截图，确认目标元素存在
2. 🔍 结构分析：使用 get_dom_tree() 或 get_page_text() 分析页面结构
3. 🎯 精确定位：使用 find_elements() 或 get_element_text() 获取精确的元素信息
4. ✅ 执行操作：基于准确信息构建选择器，执行点击、输入等操作

🚫 严禁行为：
- 禁止猜测或编造元素名称、ID、类名
- 禁止在未确认元素存在的情况下直接操作
- 禁止跳过预处理步骤直接使用选择器

🎯 选择器优先级（按推荐顺序）：
1. ID选择器：#element-id
2. CSS类选择器：.class-name
3. 属性选择器：[data-testid="value"]
4. XPath选择器：//div[@class="example"]
5. 文本匹配：仅作为辅助手段

💡 针对非多模态LLM的特别说明：
- 如果你具备图片理解能力，请结合截图进行更精确的元素定位
- 如果你不具备图片理解能力，请更加依赖文本描述和DOM结构分析
- 务必使用 get_page_text() 和 get_dom_tree() 获取详细的页面文本信息

🔄 错误处理：
- 元素未找到时，先检查页面是否完全加载
- 使用 find_elements() 验证选择器的有效性
- 考虑使用等待机制或重试策略

📊 性能优化：
- 批量操作时考虑使用智能反馈（smart_feedback=True）
- 避免重复的DOM查询操作
- 利用浏览器内置缓存机制提升页面加载速度
"""

# 默认配置
DEFAULT_CONFIG = {
    "browser": {
        "headless": False,
        "window_size": (1920, 1080),
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "timeout": 30,
        "page_load_strategy": "normal",
        "disable_images": False,
        "disable_javascript": False,
        "proxy": None,
        "download_path": None,
        "extensions": [],
        "arguments": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-web-security",
            "--allow-running-insecure-content"
        ]
    },
    "screenshot": {
        "default_format": "png",
        "quality": 90,
        "full_page": False,
        "save_path": "screenshots",
        "filename_template": "screenshot_{timestamp}",
        "max_files": 100,
        "auto_cleanup": True
    },
    "network": {
        "enable_monitoring": True,
        "response_filter": {
            "mime_types": ["text/html", "application/json", "text/plain"],
            "url_keywords": [],
            "status_codes": [200, 201, 202, 204]
        },
        "request_timeout": 30,
        "max_redirects": 10,
        "cache_disabled": False
    },
    "dom": {
        "max_depth": 10,
        "include_hidden": False,
        "skip_tags": ["script", "style", "meta", "link", "title", "head"],
        "max_text_length": 50,
        "max_children": 1000
    },
    "file": {
        "download_timeout": 60,
        "max_file_size_mb": 100,
        "allowed_extensions": [".txt", ".json", ".csv", ".xml", ".html", ".pdf", ".png", ".jpg", ".jpeg"],
        "save_path": "downloads",
        "auto_rename": True
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_path": "logs/drissionpage_mcp.log",
        "max_file_size_mb": 10,
        "backup_count": 5
    },
    "performance": {
        "element_wait_timeout": 10,
        "page_load_timeout": 30,
        "script_timeout": 30,
        "implicit_wait": 0,
        "polling_interval": 0.5,
        "max_retry_attempts": 3
    }
}

# MCP工具指令配置
INSTRUCTIONS = {
    "browser_management": {
        "connect_browser": {
            "name": "connect_browser",
            "description": "连接到现有浏览器实例或启动新的浏览器",
            "parameters": {
                "port": {"type": "integer", "description": "浏览器调试端口", "default": 9222},
                "headless": {"type": "boolean", "description": "是否无头模式", "default": False},
                "user_data_dir": {"type": "string", "description": "用户数据目录", "required": False}
            }
        },
        "new_tab": {
            "name": "new_tab",
            "description": "创建新的浏览器标签页",
            "parameters": {
                "url": {"type": "string", "description": "要打开的URL", "required": False}
            }
        },
        "close_tab": {
            "name": "close_tab",
            "description": "关闭当前标签页",
            "parameters": {}
        },
        "navigate": {
            "name": "navigate",
            "description": "导航到指定URL",
            "parameters": {
                "url": {"type": "string", "description": "目标URL", "required": True}
            }
        }
    },
    "element_operations": {
        "click_element": {
            "name": "click_element",
            "description": "点击页面元素",
            "parameters": {
                "selector": {"type": "string", "description": "CSS选择器或XPath", "required": True},
                "selector_type": {"type": "string", "enum": ["css", "xpath", "text"], "default": "css"},
                "index": {"type": "integer", "description": "元素索引（多个匹配时）", "default": 0}
            }
        },
        "input_text": {
            "name": "input_text",
            "description": "在输入框中输入文本",
            "parameters": {
                "selector": {"type": "string", "description": "输入框选择器", "required": True},
                "text": {"type": "string", "description": "要输入的文本", "required": True},
                "clear_first": {"type": "boolean", "description": "是否先清空", "default": True}
            }
        },
        "get_element_text": {
            "name": "get_element_text",
            "description": "获取元素文本内容",
            "parameters": {
                "selector": {"type": "string", "description": "元素选择器", "required": True}
            }
        },
        "get_element_attribute": {
            "name": "get_element_attribute",
            "description": "获取元素属性值",
            "parameters": {
                "selector": {"type": "string", "description": "元素选择器", "required": True},
                "attribute": {"type": "string", "description": "属性名", "required": True}
            }
        }
    },
    "page_operations": {
        "get_page_source": {
            "name": "get_page_source",
            "description": "获取页面源码",
            "parameters": {}
        },
        "get_page_title": {
            "name": "get_page_title",
            "description": "获取页面标题",
            "parameters": {}
        },
        "get_current_url": {
            "name": "get_current_url",
            "description": "获取当前页面URL",
            "parameters": {}
        },
        "scroll_page": {
            "name": "scroll_page",
            "description": "滚动页面",
            "parameters": {
                "direction": {"type": "string", "enum": ["up", "down", "left", "right"], "default": "down"},
                "distance": {"type": "integer", "description": "滚动距离（像素）", "default": 500}
            }
        }
    },
    "screenshot_operations": {
        "take_screenshot": {
            "name": "take_screenshot",
            "description": "截取页面截图",
            "parameters": {
                "filename": {"type": "string", "description": "文件名", "required": False},
                "full_page": {"type": "boolean", "description": "是否全页面截图", "default": False},
                "element_selector": {"type": "string", "description": "元素选择器（截取特定元素）", "required": False}
            }
        },
        "get_screenshot_data": {
            "name": "get_screenshot_data",
            "description": "获取截图二进制数据",
            "parameters": {
                "format": {"type": "string", "enum": ["png", "jpeg"], "default": "png"}
            }
        }
    },
    "network_operations": {
        "enable_network_monitoring": {
            "name": "enable_network_monitoring",
            "description": "启用网络监控",
            "parameters": {
                "filter_types": {"type": "array", "items": {"type": "string"}, "description": "过滤的MIME类型", "required": False}
            }
        },
        "get_network_logs": {
            "name": "get_network_logs",
            "description": "获取网络请求日志",
            "parameters": {
                "limit": {"type": "integer", "description": "返回记录数限制", "default": 50}
            }
        },
        "clear_network_logs": {
            "name": "clear_network_logs",
            "description": "清空网络日志",
            "parameters": {}
        }
    },
    "dom_operations": {
        "get_dom_tree": {
            "name": "get_dom_tree",
            "description": "获取DOM树结构",
            "parameters": {
                "selector": {"type": "string", "description": "根元素选择器", "default": "body"},
                "max_depth": {"type": "integer", "description": "最大深度", "default": 10}
            }
        },
        "find_elements": {
            "name": "find_elements",
            "description": "查找页面元素",
            "parameters": {
                "selector": {"type": "string", "description": "选择器", "required": True},
                "selector_type": {"type": "string", "enum": ["css", "xpath", "text"], "default": "css"}
            }
        }
    },
    "file_operations": {
        "save_page_source": {
            "name": "save_page_source",
            "description": "保存页面源码到文件",
            "parameters": {
                "filename": {"type": "string", "description": "文件名", "required": False}
            }
        },
        "download_file": {
            "name": "download_file",
            "description": "下载文件",
            "parameters": {
                "url": {"type": "string", "description": "文件URL", "required": True},
                "filename": {"type": "string", "description": "保存文件名", "required": False}
            }
        }
    }
}

# 环境变量配置
ENVIRONMENT_VARIABLES = {
    "DRISSIONPAGE_MCP_LOG_LEVEL": "INFO",
    "DRISSIONPAGE_MCP_BROWSER_PATH": None,
    "DRISSIONPAGE_MCP_DOWNLOAD_PATH": None,
    "DRISSIONPAGE_MCP_SCREENSHOT_PATH": None,
    "DRISSIONPAGE_MCP_HEADLESS": "false",
    "DRISSIONPAGE_MCP_TIMEOUT": "30"
}

# 错误消息配置
ERROR_MESSAGES = {
    "browser_not_connected": "浏览器未连接，请先连接浏览器",
    "element_not_found": "未找到指定元素: {selector}",
    "timeout_error": "操作超时: {operation}",
    "invalid_selector": "无效的选择器: {selector}",
    "file_not_found": "文件不存在: {filepath}",
    "permission_denied": "权限不足: {operation}",
    "network_error": "网络错误: {details}",
    "javascript_error": "JavaScript执行错误: {error}",
    "cdp_error": "CDP命令执行失败: {command}",
    "invalid_url": "无效的URL: {url}"
}

# 成功消息配置
SUCCESS_MESSAGES = {
    "browser_connected": "浏览器连接成功",
    "element_clicked": "元素点击成功",
    "text_input_success": "文本输入成功",
    "screenshot_saved": "截图保存成功: {filepath}",
    "file_downloaded": "文件下载成功: {filepath}",
    "page_navigated": "页面导航成功: {url}",
    "network_monitoring_enabled": "网络监控已启用",
    "dom_tree_generated": "DOM树生成成功"
}


def get_config_value(key_path: str, default: Any = None) -> Any:
    """获取配置值
    
    Args:
        key_path: 配置键路径，用点分隔（如 'browser.headless'）
        default: 默认值
        
    Returns:
        Any: 配置值
    """
    try:
        keys = key_path.split('.')
        value = DEFAULT_CONFIG
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def update_config(key_path: str, value: Any) -> bool:
    """更新配置值
    
    Args:
        key_path: 配置键路径
        value: 新值
        
    Returns:
        bool: 是否更新成功
    """
    try:
        keys = key_path.split('.')
        config = DEFAULT_CONFIG
        for key in keys[:-1]:
            config = config[key]
        config[keys[-1]] = value
        return True
    except (KeyError, TypeError):
        return False


def get_env_config() -> Dict[str, Any]:
    """从环境变量获取配置
    
    Returns:
        dict: 环境配置
    """
    env_config = {}
    for key, default_value in ENVIRONMENT_VARIABLES.items():
        env_value = os.getenv(key, default_value)
        
        # 类型转换
        if key.endswith('_HEADLESS'):
            env_config[key] = env_value.lower() in ('true', '1', 'yes')
        elif key.endswith('_TIMEOUT'):
            try:
                env_config[key] = int(env_value)
            except (ValueError, TypeError):
                env_config[key] = default_value
        else:
            env_config[key] = env_value
    
    return env_config


def get_work_directory() -> Path:
    """获取工作目录
    
    Returns:
        Path: 工作目录路径
    """
    return Path.cwd()


def get_drissionpage_mcp_directory() -> Path:
    """获取DrissionPage MCP专用目录
    
    Returns:
        Path: DrissionPage MCP目录路径
    """
    import os
    # 使用用户主目录下的drissionpage_mcp目录
    base_dir = Path.home() / "drissionpage_mcp"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_screenshots_directory() -> Path:
    """获取截图目录
    
    Returns:
        Path: 截图目录路径
    """
    base_dir = get_drissionpage_mcp_directory()
    screenshots_dir = base_dir / "screenshot"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    return screenshots_dir


def get_downloads_directory() -> Path:
    """获取下载目录
    
    Returns:
        Path: 下载目录路径
    """
    base_dir = get_drissionpage_mcp_directory()
    downloads_dir = base_dir / "file" / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    return downloads_dir


def get_logs_directory() -> Path:
    """获取日志目录
    
    Returns:
        Path: 日志目录路径
    """
    base_dir = get_drissionpage_mcp_directory()
    logs_dir = base_dir / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_cookies_directory() -> Path:
    """获取Cookies存储目录
    
    Returns:
        Path: Cookies目录路径
    """
    base_dir = get_drissionpage_mcp_directory()
    cookies_dir = base_dir / "file" / "cookies"
    cookies_dir.mkdir(parents=True, exist_ok=True)
    return cookies_dir


def get_page_source_directory() -> Path:
    """获取页面源码存储目录
    
    Returns:
        Path: 页面源码目录路径
    """
    base_dir = get_drissionpage_mcp_directory()
    page_source_dir = base_dir / "file" / "page_source"
    page_source_dir.mkdir(parents=True, exist_ok=True)
    return page_source_dir


def validate_config() -> List[str]:
    """验证配置
    
    Returns:
        list: 验证错误列表
    """
    errors = []
    
    # 验证浏览器配置
    browser_config = get_config_value('browser', {})
    if not isinstance(browser_config.get('timeout'), (int, float)) or browser_config.get('timeout') <= 0:
        errors.append("浏览器超时配置无效")
    
    # 验证截图配置
    screenshot_config = get_config_value('screenshot', {})
    if screenshot_config.get('quality', 90) < 1 or screenshot_config.get('quality', 90) > 100:
        errors.append("截图质量配置无效（应在1-100之间）")
    
    # 验证文件配置
    file_config = get_config_value('file', {})
    if not isinstance(file_config.get('max_file_size_mb'), (int, float)) or file_config.get('max_file_size_mb') <= 0:
        errors.append("文件大小限制配置无效")
    
    return errors