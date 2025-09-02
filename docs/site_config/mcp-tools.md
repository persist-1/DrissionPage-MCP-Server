# MCP工具文档

## 概述

DrissionPage MCP Server 提供了丰富的浏览器自动化工具，基于 DrissionPage 和 FastMCP 框架构建。本文档详细介绍了所有可用的 MCP 工具及其使用方法。

## 工具分类

### 🌐 浏览器管理工具

#### connect_browser
连接到现有浏览器实例或启动新的浏览器。

**参数：**
- `port` (int, 可选): 浏览器调试端口，默认 9222
- `headless` (bool, 可选): 是否无头模式，默认 False
- `user_data_dir` (str, 可选): 用户数据目录路径

**返回：** 浏览器连接状态信息

**示例：**
```python
# 连接到默认端口的浏览器
connect_browser()

# 连接到指定端口的无头浏览器
connect_browser(port=9223, headless=True)

# 使用自定义用户数据目录
connect_browser(user_data_dir="/path/to/userdata")
```

#### new_tab
创建新的浏览器标签页。

**参数：**
- `url` (str, 可选): 新标签页要打开的URL

**返回：** 新标签页创建结果

**示例：**
```python
# 创建空白标签页
new_tab()

# 创建并导航到指定URL
new_tab(url="https://example.com")
```

#### navigate
导航到指定URL。

**参数：**
- `url` (str, 必需): 目标URL

**返回：** 导航结果信息

**示例：**
```python
navigate(url="https://www.google.com")
```

### 🎯 元素操作工具

#### click_element
点击页面元素（智能优化版）。

**重要提示：** 使用前请遵循标准化工作流程：
1. 📸 先使用 `take_screenshot()` 确认目标元素存在
2. 🔍 使用 `get_dom_tree()` 或 `find_elements()` 分析页面结构
3. 🎯 基于准确信息构建选择器，禁止猜测元素名称

**参数：**
- `selector` (str, 必需): 元素选择器
- `selector_type` (str, 可选): 选择器类型 (css, xpath, text)，默认 "css"
- `index` (int, 可选): 元素索引（多个匹配时），默认 0
- `smart_feedback` (bool, 可选): 是否启用智能反馈，默认 True
- `use_cache` (bool, 可选): 是否使用缓存，默认 True

**选择器优先级：**
1. ID选择器：`#element-id` （最优先）
2. CSS类选择器：`.class-name`
3. 属性选择器：`[data-testid="value"]`
4. XPath选择器：`//div[@class="example"]`
5. 文本匹配：仅作为辅助手段

**示例：**
```python
# 点击ID为submit的按钮
click_element(selector="#submit", selector_type="css")

# 点击包含特定文本的元素
click_element(selector="提交", selector_type="text")

# 使用XPath选择器
click_element(selector="//button[@class='btn-primary']", selector_type="xpath")
```

#### input_text
在输入框中输入文本（智能优化版）。

**参数：**
- `selector` (str, 必需): 输入框选择器
- `text` (str, 必需): 要输入的文本内容
- `clear_first` (bool, 可选): 是否先清空输入框，默认 True

**示例：**
```python
# 在用户名输入框中输入文本
input_text(selector="#username", text="myusername")

# 在输入框中追加文本（不清空原内容）
input_text(selector="[name='message']", text="Hello World", clear_first=False)
```

#### get_element_text
获取元素文本内容（精确定位版）。

**参数：**
- `selector` (str, 必需): 元素选择器

**返回：** 元素的文本内容

**示例：**
```python
# 获取标题文本
get_element_text(selector="h1")

# 获取状态信息
get_element_text(selector=".status-message")
```

#### get_page_text
获取页面完整文本内容（预处理必备工具）。

**用途：**
1. 🔍 在操作元素前，获取页面的完整文本信息
2. 📋 为非多模态LLM提供详细的页面内容描述
3. 🎯 帮助构建精确的元素选择器
4. ✅ 确认页面加载完成和内容可用性

**返回：** 页面的完整可见文本内容（去除HTML标签）

**示例：**
```python
# 获取当前页面的所有文本内容
page_content = get_page_text()
```

### 📸 截图工具

#### take_screenshot
截取页面截图（标准化工作流程第1步）。

**参数：**
- `filename` (str, 可选): 截图文件名，自动生成时间戳命名
- `full_page` (bool, 可选): 是否截取完整页面，默认 False（可视区域）
- `element_selector` (str, 可选): 仅截取特定元素

**返回：** 截图保存路径和操作结果

**示例：**
```python
# 截取可视区域
take_screenshot()

# 截取完整页面
take_screenshot(full_page=True)

# 截取特定元素
take_screenshot(element_selector="#main-content")

# 指定文件名
take_screenshot(filename="login_page.png")
```

#### get_screenshot_data
获取截图二进制数据。

**参数：**
- `format` (str, 可选): 图片格式，默认 "png"

**返回：** 截图的二进制数据

**示例：**
```python
# 获取PNG格式的截图数据
screenshot_data = get_screenshot_data(format="png")
```

### 🌳 DOM操作工具

#### get_dom_tree
获取DOM树结构（结构化分析工具）。

**参数：**
- `selector` (str, 可选): 起始选择器，默认 "body"
- `max_depth` (int, 可选): 最大遍历深度，默认 10

**返回：** 结构化的DOM树信息

**示例：**
```python
# 获取整个页面的DOM结构
get_dom_tree()

# 获取特定区域的DOM结构
get_dom_tree(selector="#main-content", max_depth=5)
```

#### find_elements
查找页面元素（智能定位工具）。

**参数：**
- `selector` (str, 必需): 元素选择器
- `selector_type` (str, 可选): 选择器类型 (css, xpath, text)，默认 "css"
- `limit` (int, 可选): 返回元素数量限制，默认 10
- `include_similar` (bool, 可选): 是否包含相似元素，默认 True

**返回：** 匹配元素的详细信息列表

**示例：**
```python
# 查找所有按钮元素
find_elements(selector="button", selector_type="css")

# 查找包含特定文本的元素
find_elements(selector="登录", selector_type="text", limit=5)

# 使用XPath查找元素
find_elements(selector="//input[@type='text']", selector_type="xpath")
```

### 🌐 网络监控工具

#### enable_network_monitoring
启用网络监控。

**参数：**
- `filter_types` (List[str], 可选): 需要监听的mimeType类型列表

**返回：** 启用结果

**示例：**
```python
# 启用所有网络监控
enable_network_monitoring()

# 只监控JSON和图片请求
enable_network_monitoring(filter_types=["application/json", "image/png"])
```

#### get_network_logs
获取网络请求日志。

**参数：**
- `limit` (int, 可选): 返回日志的最大数量，默认 50

**返回：** 网络日志数据

**示例：**
```python
# 获取最近50条网络日志
get_network_logs()

# 获取最近100条网络日志
get_network_logs(limit=100)
```

### 📁 文件操作工具

#### save_page_source
保存页面源码到文件。

**参数：**
- `filename` (str, 可选): 保存文件名，自动生成时间戳命名

**返回：** 保存结果信息

**示例：**
```python
# 保存当前页面源码
save_page_source()

# 指定文件名保存
save_page_source(filename="homepage.html")
```

#### get_cookies
获取当前页面的Cookies。

**返回：** 当前页面的所有Cookie信息

**示例：**
```python
# 获取当前页面的所有Cookie
cookies = get_cookies()
```

### ⚡ JavaScript执行工具

#### execute_javascript
执行JavaScript代码。

**参数：**
- `code` (str, 必需): 要执行的JavaScript代码
- `return_result` (bool, 可选): 是否返回执行结果，默认 True

**返回：** JavaScript执行结果

**示例：**
```python
# 执行简单的JavaScript代码
execute_javascript(code="document.title")

# 执行复杂的JavaScript操作
execute_javascript(code="""
    const elements = document.querySelectorAll('.item');
    return elements.length;
""")

# 修改页面元素
execute_javascript(code="document.getElementById('myButton').click()")
```

### 🔧 CDP命令工具

#### run_cdp_command
执行Chrome DevTools Protocol命令。

**参数：**
- `command` (str, 必需): CDP命令名称
- `**params`: CDP命令参数

**返回：** CDP命令执行结果

**示例：**
```python
# 停止页面加载
run_cdp_command(command="Page.stopLoading")

# 导航到指定URL
run_cdp_command(command="Page.navigate", url="https://example.com")

# 获取页面性能指标
run_cdp_command(command="Performance.getMetrics")
```

## 最佳实践工作流程

### 标准化操作流程

1. **📸 视觉确认** - 使用 `take_screenshot()` 获取页面截图
2. **📄 文本分析** - 使用 `get_page_text()` 获取页面文本内容
3. **🌳 结构分析** - 使用 `get_dom_tree()` 分析页面DOM结构
4. **🔍 元素定位** - 使用 `find_elements()` 精确定位目标元素
5. **🎯 执行操作** - 使用 `click_element()` 或 `input_text()` 执行具体操作

### 选择器构建原则

1. **优先级顺序：**
   - ID选择器：`#element-id`
   - CSS类选择器：`.class-name`
   - 属性选择器：`[data-testid="value"]`
   - XPath选择器：`//div[@class="example"]`
   - 文本匹配：仅作为辅助手段

2. **禁止行为：**
   - 禁止猜测元素名称或选择器
   - 禁止使用未经验证的选择器
   - 禁止跳过预处理步骤直接操作

### 错误处理和调试

1. **操作失败时：**
   - 重新截图确认页面状态
   - 检查DOM结构是否发生变化
   - 验证选择器是否仍然有效
   - 查看网络日志排查异步加载问题

2. **性能优化：**
   - 启用缓存机制 (`use_cache=True`)
   - 合理设置元素查找限制 (`limit`)
   - 适当控制DOM树深度 (`max_depth`)

## 配置和环境

### 环境变量

- `DRISSIONPAGE_MCP_LOG_LEVEL`: 日志级别，默认 "INFO"
- `DRISSIONPAGE_MCP_BROWSER_PATH`: 浏览器可执行文件路径
- `DRISSIONPAGE_MCP_DOWNLOAD_PATH`: 下载文件保存路径
- `DRISSIONPAGE_MCP_SCREENSHOT_PATH`: 截图保存路径
- `DRISSIONPAGE_MCP_HEADLESS`: 是否启用无头模式，默认 "false"
- `DRISSIONPAGE_MCP_TIMEOUT`: 操作超时时间，默认 "30"

### 默认配置

```json
{
  "browser": {
    "debug_port": 9222,
    "headless": false,
    "window_size": [1920, 1080],
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  },
  "screenshot": {
    "format": "png",
    "quality": 90,
    "full_page": false
  },
  "performance": {
    "element_wait_timeout": 10,
    "page_load_timeout": 30,
    "script_timeout": 30
  }
}
```

## 常见问题

### Q: 如何处理动态加载的内容？
A: 使用网络监控工具监听AJAX请求，结合适当的等待策略和重试机制。

### Q: 选择器失效怎么办？
A: 重新分析DOM结构，使用更稳定的选择器（如ID或data属性），避免依赖易变的class名称。

### Q: 如何提高操作成功率？
A: 严格遵循标准化工作流程，充分利用预处理工具，避免盲目猜测元素选择器。

### Q: 无头模式下截图异常？
A: 确保设置了合适的窗口大小，某些页面在无头模式下渲染可能有差异。

---