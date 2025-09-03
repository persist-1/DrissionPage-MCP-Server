# API 参考

本文档详细介绍 DrissionPage-MCP-Server 提供的所有 MCP 工具及其使用方法。

## 工具概览

| 分类 | 工具数量 | 主要功能 |
|------|----------|----------|
| 🌐 浏览器管理 | 3 | 浏览器连接、标签页管理、页面导航 |
| 🎯 元素操作 | 3 | 点击、输入、文本获取 |
| 📸 截图功能 | 2 | 页面截图、数据获取 |
| 🌳 DOM操作 | 3 | DOM树获取、元素查找、页面文本 |
| 🔍 网络监控 | 2 | 网络监听、日志获取 |
| 📁 文件操作 | 2 | 页面源码、Cookie管理 |
| ⚡ 高级功能 | 2 | JavaScript执行、CDP命令 |

## 浏览器管理

### connect_browser

连接到现有浏览器或启动新的浏览器实例。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `port` | `int` | `9222` | 浏览器调试端口 |
| `headless` | `bool` | `false` | 是否以无头模式运行 |
| `user_data_dir` | `str` | `null` | 用户数据目录路径 |

**返回值：**
```json
{
  "success": true,
  "message": "成功连接到浏览器",
  "browser_info": {
    "version": "Chrome/120.0.0.0",
    "port": 9222,
    "headless": false
  }
}
```

**使用示例：**
```python
# 连接到默认端口的浏览器
result = await connect_browser()

# 连接到指定端口的无头浏览器
result = await connect_browser(port=9223, headless=True)

# 使用自定义用户数据目录
result = await connect_browser(user_data_dir="/path/to/profile")
```

### new_tab

创建新的浏览器标签页。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `url` | `str` | `null` | 新标签页要打开的URL |

**返回值：**
```json
{
  "success": true,
  "message": "成功创建新标签页",
  "tab_info": {
    "tab_id": "tab_123",
    "url": "https://example.com"
  }
}
```

**使用示例：**
```python
# 创建空白标签页
result = await new_tab()

# 创建并导航到指定URL
result = await new_tab(url="https://example.com")
```

### navigate

导航到指定的URL。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `url` | `str` | - | 目标URL（必需） |

**返回值：**
```json
{
  "success": true,
  "message": "成功导航到 https://example.com",
  "page_info": {
    "title": "Example Domain",
    "url": "https://example.com",
    "load_time": 1.23
  }
}
```

**使用示例：**
```python
# 导航到网页
result = await navigate("https://example.com")

# 导航到本地文件
result = await navigate("file:///path/to/local.html")
```

## 元素操作

### click_element

点击页面上的元素。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `selector` | `str` | - | 元素选择器（必需） |
| `selector_type` | `str` | `"css"` | 选择器类型：css/xpath/text |
| `index` | `int` | `0` | 元素索引（多个匹配时） |
| `smart_feedback` | `bool` | `true` | 启用智能反馈 |

**返回值：**
```json
{
  "success": true,
  "message": "成功点击元素: #submit-btn",
  "element_info": {
    "selector": "#submit-btn",
    "text": "提交",
    "tag_name": "button"
  }
}
```

**使用示例：**
```python
# CSS选择器点击
result = await click_element("#submit-button")

# XPath选择器点击
result = await click_element("//button[@type='submit']", selector_type="xpath")

# 文本匹配点击
result = await click_element("提交", selector_type="text")

# 点击第二个匹配的元素
result = await click_element(".item", index=1)
```

### input_text

在输入框中输入文本。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `selector` | `str` | - | 输入框选择器（必需） |
| `text` | `str` | - | 要输入的文本（必需） |
| `clear_first` | `bool` | `true` | 是否先清空输入框 |

**返回值：**
```json
{
  "success": true,
  "message": "成功输入文本到 #username",
  "input_info": {
    "selector": "#username",
    "text_length": 12,
    "cleared_first": true
  }
}
```

**使用示例：**
```python
# 基本文本输入
result = await input_text("#username", "john_doe")

# 追加文本（不清空）
result = await input_text("#message", "Hello World", clear_first=False)

# 输入特殊字符
result = await input_text("#password", "P@ssw0rd123!")
```

### get_element_text

获取元素的文本内容。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `selector` | `str` | - | 元素选择器（必需） |

**返回值：**
```json
{
  "success": true,
  "text": "Welcome to our website",
  "element_info": {
    "selector": ".title",
    "tag_name": "h1",
    "visible": true
  }
}
```

**使用示例：**
```python
# 获取标题文本
result = await get_element_text(".title")

# 获取按钮文本
result = await get_element_text("#submit-btn")

# 获取表格单元格文本
result = await get_element_text("table tr:first-child td:nth-child(2)")
```

## 截图功能

### take_screenshot

截取页面或元素的截图。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `filename` | `str` | `null` | 截图文件名（自动生成） |
| `full_page` | `bool` | `false` | 是否截取完整页面 |
| `element_selector` | `str` | `null` | 仅截取特定元素 |

**返回值：**
```json
{
  "success": true,
  "message": "截图已保存",
  "screenshot_info": {
    "filename": "screenshot_20240101_120000.png",
    "path": "/path/to/screenshot.png",
    "size": {
      "width": 1920,
      "height": 1080
    },
    "file_size": "245KB"
  }
}
```

**使用示例：**
```python
# 截取当前视口
result = await take_screenshot()

# 截取完整页面
result = await take_screenshot(full_page=True)

# 截取特定元素
result = await take_screenshot(element_selector=".content")

# 自定义文件名
result = await take_screenshot(filename="my_screenshot.png")
```

### get_screenshot_data

获取截图的二进制数据。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `format` | `str` | `"png"` | 图片格式：png/jpeg/webp |

**返回值：**
```json
{
  "success": true,
  "data": "base64_encoded_image_data",
  "format": "png",
  "size": {
    "width": 1920,
    "height": 1080
  }
}
```

**使用示例：**
```python
# 获取PNG格式数据
result = await get_screenshot_data()

# 获取JPEG格式数据
result = await get_screenshot_data(format="jpeg")
```

## DOM操作

### get_dom_tree

获取页面的DOM树结构。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `selector` | `str` | `"body"` | 起始选择器 |
| `max_depth` | `int` | `10` | 最大遍历深度 |

**返回值：**
```json
{
  "success": true,
  "dom_tree": "<body>\n  <div class='container'>\n    <h1>Title</h1>\n  </div>\n</body>",
  "stats": {
    "total_elements": 156,
    "max_depth_reached": 8,
    "processing_time": 0.45
  }
}
```

**使用示例：**
```python
# 获取完整页面DOM
result = await get_dom_tree()

# 获取特定容器的DOM
result = await get_dom_tree(selector=".main-content")

# 限制遍历深度
result = await get_dom_tree(max_depth=5)
```

### find_elements

查找页面中的元素。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `selector` | `str` | - | 元素选择器（必需） |
| `selector_type` | `str` | `"css"` | 选择器类型：css/xpath/text |
| `limit` | `int` | `10` | 返回元素数量限制 |
| `include_similar` | `bool` | `true` | 包含相似元素 |

**返回值：**
```json
{
  "success": true,
  "elements": [
    {
      "selector": ".item:nth-child(1)",
      "text": "Item 1",
      "attributes": {
        "class": "item active",
        "id": "item-1"
      },
      "position": {
        "x": 100,
        "y": 200
      }
    }
  ],
  "total_found": 5,
  "search_time": 0.12
}
```

**使用示例：**
```python
# 查找所有按钮
result = await find_elements("button")

# 使用XPath查找
result = await find_elements("//div[@class='item']", selector_type="xpath")

# 限制返回数量
result = await find_elements(".product", limit=5)
```

### get_page_text

获取页面的完整文本内容。

**参数：** 无

**返回值：**
```json
{
  "success": true,
  "text": "Welcome to our website\nThis is the main content...",
  "stats": {
    "character_count": 1234,
    "word_count": 200,
    "line_count": 45
  }
}
```

**使用示例：**
```python
# 获取页面所有文本
result = await get_page_text()
```

## 网络监控

### enable_network_monitoring

启用网络请求监控。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `filter_types` | `list` | `null` | 过滤的MIME类型列表 |

**返回值：**
```json
{
  "success": true,
  "message": "网络监控已启用",
  "config": {
    "filter_types": ["application/json", "text/html"],
    "max_logs": 1000
  }
}
```

**使用示例：**
```python
# 启用所有类型监控
result = await enable_network_monitoring()

# 只监控JSON和HTML
result = await enable_network_monitoring(
    filter_types=["application/json", "text/html"]
)
```

### get_network_logs

获取网络请求日志。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `limit` | `int` | `50` | 返回日志的最大数量 |

**返回值：**
```json
{
  "success": true,
  "logs": [
    {
      "url": "https://api.example.com/data",
      "method": "GET",
      "status": 200,
      "response_time": 245,
      "content_type": "application/json",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "total_logs": 25
}
```

**使用示例：**
```python
# 获取最近50条日志
result = await get_network_logs()

# 获取最近10条日志
result = await get_network_logs(limit=10)
```

## 文件操作

### save_page_source

保存页面源码到文件。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `filename` | `str` | `null` | 文件名（自动生成） |

**返回值：**
```json
{
  "success": true,
  "message": "页面源码已保存",
  "file_info": {
    "filename": "page_source_20240101_120000.html",
    "path": "/path/to/source.html",
    "size": "45KB",
    "encoding": "utf-8"
  }
}
```

**使用示例：**
```python
# 保存当前页面源码
result = await save_page_source()

# 自定义文件名
result = await save_page_source(filename="my_page.html")
```

### get_cookies

获取当前页面的Cookies。

**参数：** 无

**返回值：**
```json
{
  "success": true,
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": ".example.com",
      "path": "/",
      "expires": "2024-12-31T23:59:59Z",
      "secure": true,
      "httpOnly": true
    }
  ],
  "total_cookies": 5
}
```

**使用示例：**
```python
# 获取所有Cookies
result = await get_cookies()
```

## 高级功能

### execute_javascript

在页面中执行JavaScript代码。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `code` | `str` | - | JavaScript代码（必需） |
| `return_result` | `bool` | `true` | 是否返回执行结果 |

**返回值：**
```json
{
  "success": true,
  "result": "Hello World",
  "execution_time": 0.05,
  "type": "string"
}
```

**使用示例：**
```python
# 执行简单JavaScript
result = await execute_javascript("return document.title;")

# 执行复杂操作
code = """
const elements = document.querySelectorAll('.item');
return Array.from(elements).map(el => el.textContent);
"""
result = await execute_javascript(code)

# 不返回结果的操作
result = await execute_javascript(
    "console.log('Debug message');",
    return_result=False
)
```

### run_cdp_command

执行Chrome DevTools Protocol命令。

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `command` | `str` | - | CDP命令名称（必需） |
| `params` | `str` | - | 命令参数（JSON字符串，必需） |

**返回值：**
```json
{
  "success": true,
  "result": {
    "frameId": "frame_123",
    "loaderId": "loader_456"
  },
  "command": "Page.reload",
  "execution_time": 0.15
}
```

**使用示例：**
```python
# 重新加载页面
result = await run_cdp_command("Page.reload", "{}")

# 设置用户代理
params = '{"userAgent": "Custom User Agent 1.0"}'
result = await run_cdp_command("Network.setUserAgentOverride", params)

# 获取页面信息
result = await run_cdp_command("Page.getFrameTree", "{}")
```

## MCP 资源

除了工具外，服务器还提供以下资源：

### config://default

获取默认配置信息。

**返回值：**
```json
{
  "browser": {
    "headless": false,
    "port": 9222,
    "timeout": 30
  },
  "screenshot": {
    "format": "png",
    "path": "./screenshots"
  }
}
```

### instructions://all

获取所有工具的使用指令。

**返回值：**
```text
DrissionPage-MCP-Server 工具使用指南

1. 浏览器管理
   - connect_browser: 连接浏览器
   - new_tab: 创建新标签页
   - navigate: 页面导航

...
```

### status://browser

获取浏览器状态信息。

**返回值：**
```json
{
  "connected": true,
  "version": "Chrome/120.0.0.0",
  "tabs_count": 3,
  "active_tab": "tab_123",
  "memory_usage": "245MB"
}
```

## 错误处理

所有工具都遵循统一的错误处理格式：

```json
{
  "success": false,
  "error": {
    "code": "ELEMENT_NOT_FOUND",
    "message": "无法找到指定的元素",
    "details": {
      "selector": "#non-existent",
      "selector_type": "css",
      "retry_count": 3
    }
  }
}
```

### 常见错误代码

| 错误代码 | 描述 | 解决方案 |
|----------|------|----------|
| `BROWSER_NOT_CONNECTED` | 浏览器未连接 | 先调用 connect_browser |
| `ELEMENT_NOT_FOUND` | 元素未找到 | 检查选择器或等待页面加载 |
| `TIMEOUT_ERROR` | 操作超时 | 增加超时时间或检查网络 |
| `INVALID_SELECTOR` | 选择器无效 | 检查选择器语法 |
| `PERMISSION_DENIED` | 权限不足 | 检查文件/目录权限 |

## 最佳实践

### 1. 选择器优化

```python
# 推荐：使用具体的选择器
result = await click_element("#submit-button")

# 避免：过于宽泛的选择器
result = await click_element("button")  # 可能匹配多个元素
```

### 2. 错误处理

```python
# 推荐：检查操作结果
result = await click_element("#button")
if not result.get("success"):
    print(f"操作失败: {result.get('error', {}).get('message')}")
```

### 3. 性能优化

```python
# 推荐：合理设置限制
result = await find_elements(".item", limit=20)
```

### 4. 资源管理

```python
# 推荐：及时清理截图
result = await take_screenshot()
# 处理完截图后删除文件

# 推荐：关闭不需要的标签页
# 避免打开过多标签页消耗内存
```

---

更多使用示例和高级用法，请参考 [使用说明](./instruction.md) 。