# -*- coding: utf-8 -*-
"""工具函数模块

提供通用的工具函数。
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
import time
import os


def get_dom_tree_json(tab, selector: str = "body", max_depth: int = 10) -> str:
    """获取DOM树的JSON表示
    
    Args:
        tab: ChromiumTab实例
        selector: CSS选择器，默认为body
        max_depth: 最大遍历深度
        
    Returns:
        str: DOM树的JSON字符串
    """
    try:
        # 执行JavaScript获取DOM树
        js_code = f"""
        function isVisuallyHidden(element) {{
            const style = window.getComputedStyle(element);
            return style.display === 'none' || 
                   style.visibility === 'hidden' || 
                   style.opacity === '0' ||
                   element.offsetWidth === 0 || 
                   element.offsetHeight === 0;
        }}
        
        function getNodeLabel(node) {{
            let label = node.tagName ? node.tagName.toLowerCase() : node.nodeName.toLowerCase();
            
            if (node.id) {{
                label += '#' + node.id;
            }}
            
            if (node.className && typeof node.className === 'string') {{
                const classes = node.className.trim().split(/\\s+/).slice(0, 3);
                if (classes.length > 0 && classes[0]) {{
                    label += '.' + classes.join('.');
                }}
            }}
            
            if (node.nodeType === Node.TEXT_NODE) {{
                const text = node.textContent.trim();
                if (text) {{
                    label += ': "' + text.substring(0, 50) + (text.length > 50 ? '...' : '') + '"';
                }}
            }}
            
            return label;
        }}
        
        function buildDomJsonTree(node, depth = 0, maxDepth = 10) {{
            if (depth > maxDepth) return null;
            
            const skipTags = ['script', 'style', 'meta', 'link', 'title', 'head'];
            if (node.tagName && skipTags.includes(node.tagName.toLowerCase())) {{
                return null;
            }}
            
            if (node.nodeType === Node.ELEMENT_NODE && isVisuallyHidden(node)) {{
                return null;
            }}
            
            const nodeInfo = {{
                label: getNodeLabel(node),
                type: node.nodeType,
                tagName: node.tagName || null,
                id: node.id || null,
                className: node.className || null,
                children: []
            }};
            
            if (node.nodeType === Node.TEXT_NODE) {{
                const text = node.textContent.trim();
                if (!text) return null;
                nodeInfo.text = text;
                return nodeInfo;
            }}
            
            for (let child of node.childNodes) {{
                const childNode = buildDomJsonTree(child, depth + 1, maxDepth);
                if (childNode) {{
                    nodeInfo.children.push(childNode);
                }}
            }}
            
            return nodeInfo;
        }}
        
        const rootElement = document.querySelector('{selector}');
        if (!rootElement) {{
            return JSON.stringify({{error: 'Element not found'}});
        }}
        
        const domTree = buildDomJsonTree(rootElement, 0, {max_depth});
        return JSON.stringify(domTree, null, 2);
        """
        
        result = tab.run_js(js_code)
        return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"获取DOM树失败: {str(e)}"}, ensure_ascii=False, indent=2)


def save_dict_to_sqlite(data: Dict[str, Any], db_path: str, table_name: str = "data") -> str:
    """将字典数据保存到SQLite数据库
    
    Args:
        data: 要保存的字典数据
        db_path: 数据库文件路径
        table_name: 表名
        
    Returns:
        str: 保存结果
    """
    try:
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                data TEXT
            )
        ''')
        
        # 插入数据
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        cursor.execute(f'''
            INSERT INTO {table_name} (timestamp, data) VALUES (?, ?)
        ''', (timestamp, json_data))
        
        conn.commit()
        conn.close()
        
        return f"数据已保存到 {db_path} 的 {table_name} 表中"
    except Exception as e:
        return f"保存数据失败: {str(e)}"


def load_dict_from_sqlite(db_path: str, table_name: str = "data", limit: int = 10) -> List[Dict[str, Any]]:
    """从SQLite数据库加载字典数据
    
    Args:
        db_path: 数据库文件路径
        table_name: 表名
        limit: 限制返回的记录数
        
    Returns:
        list: 数据列表
    """
    try:
        if not Path(db_path).exists():
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT id, timestamp, data FROM {table_name} 
            ORDER BY id DESC LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            try:
                data = json.loads(row[2])
                results.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "data": data
                })
            except json.JSONDecodeError:
                continue
        
        conn.close()
        return results
    except Exception as e:
        return [{"error": f"加载数据失败: {str(e)}"}]


def ensure_directory(path: str) -> str:
    """确保目录存在
    
    Args:
        path: 目录路径
        
    Returns:
        str: 创建结果
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return f"目录已确保存在: {path}"
    except Exception as e:
        return f"创建目录失败: {str(e)}"


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）
    
    Args:
        file_path: 文件路径
        
    Returns:
        float: 文件大小（MB）
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return round(size_bytes / (1024 * 1024), 2)
    except Exception:
        return 0.0


def clean_old_files(directory: str, max_age_days: int = 7, pattern: str = "*") -> str:
    """清理旧文件
    
    Args:
        directory: 目录路径
        max_age_days: 最大保留天数
        pattern: 文件匹配模式
        
    Returns:
        str: 清理结果
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"目录不存在: {directory}"
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        deleted_count = 0
        deleted_size = 0
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += file_size
        
        size_mb = round(deleted_size / (1024 * 1024), 2)
        return f"已删除 {deleted_count} 个文件，释放空间 {size_mb} MB"
    except Exception as e:
        return f"清理文件失败: {str(e)}"


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """格式化时间戳
    
    Args:
        timestamp: 时间戳，如果不提供则使用当前时间
        
    Returns:
        str: 格式化的时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    return time.strftime('%Y%m%d_%H%M%S', time.localtime(timestamp))


def safe_filename(filename: str) -> str:
    """生成安全的文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    # 移除或替换不安全的字符
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # 限制长度
    if len(safe_name) > 200:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:200-len(ext)] + ext
    
    return safe_name


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个字典
    
    Args:
        *dicts: 要合并的字典
        
    Returns:
        dict: 合并后的字典
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def filter_dict_by_keys(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """根据键过滤字典
    
    Args:
        data: 原始字典
        keys: 要保留的键列表
        
    Returns:
        dict: 过滤后的字典
    """
    return {k: v for k, v in data.items() if k in keys}


def deep_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """深度获取嵌套字典的值
    
    Args:
        data: 字典数据
        path: 路径，用点分隔（如 'user.profile.name'）
        default: 默认值
        
    Returns:
        Any: 获取到的值或默认值
    """
    try:
        keys = path.split('.')
        result = data
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default


def validate_url(url: str) -> bool:
    """验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        bool: 是否为有效URL
    """
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_file_extension(filename: str) -> str:
    """获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 扩展名（不包含点）
    """
    return Path(filename).suffix.lstrip('.')


def is_image_file(filename: str) -> bool:
    """判断是否为图片文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为图片文件
    """
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'}
    return get_file_extension(filename).lower() in image_extensions


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断字符串
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        str: 截断后的字符串
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix