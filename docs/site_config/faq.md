# 常见问题 (FAQ)

本文档收集了用户在使用 DrissionPage-MCP-Server 过程中遇到的常见问题及解决方案。

## 安装和配置

### Q: 如何安装 DrissionPage-MCP-Server？

**A:** 有多种安装方式：

```bash
# 从源码安装（推荐）
git clone https://github.com/persist-1/DrissionPage-MCP-Server.git
cd DrissionPage-MCP-Server

# 同步环境
uv sync

```

### Q: 启动服务时提示 "找不到 Chrome 浏览器"？

**A:** 请确保已安装 Chrome 浏览器：

### Q: 如何在 Trae AI IDE 中配置 MCP 服务？

**A:** 按以下步骤配置：

1. 打开 Trae AI IDE 设置
2. 找到 MCP 服务配置选项
3. 添加新的 MCP 服务：
```json
   {
      "mcpServers": {
         "drissionpage-mcp": {
            "command": "Yourpath\\DrissionPage-MCP-Server\\.venv\\Scripts\\python.exe",
            "args": [
            "-m",
            "drissionpage_mcp.main"
            ],
            "env": {
            "PYTHONPATH": "Yourpath\\DrissionPage-MCP-Server\\src"
            }
         }
      }
   }
```
4. 保存配置并启动 MCP 服务

### Q: 支持哪些操作系统？

**A:** 支持以下操作系统：

- ✅ **Windows** 10/11（暂时就测了windows，本来也是为了在windows上使用，欢迎各位提交pr以支持其他操作系统）

## 浏览器相关

### Q: 浏览器连接失败怎么办？

**A:** 按以下步骤排查：

1. **检查浏览器是否运行**：
   ```bash
   # 手动启动 Chrome 调试模式
   google-chrome --remote-debugging-port=9222 --no-first-run
   ```

2. **检查端口是否被占用**：
   ```bash
   # Windows
   netstat -an | findstr :9222
   
   # Linux/macOS
   lsof -i :9222
   ```

3. **尝试不同端口**：
   ```python
   result = await connect_browser(port=9223)
   ```

### Q: 无头模式下截图失败？

**A:** 无头模式可能需要额外配置：

```bash
# 设置虚拟显示（Linux）
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# 或者使用有头模式
result = await connect_browser(headless=False)
```

### Q: 如何处理浏览器崩溃？

**A:** 实现自动重连机制：

```python
# 检查浏览器状态
status = await get_browser_status()
if not status.get("connected"):
    # 重新连接
    await connect_browser()
```

## 元素操作

### Q: 元素找不到怎么办？

**A:** 尝试以下解决方案：

1. **等待页面加载**：
   ```python
   # 先导航，再等待
   await navigate("https://example.com")
   await asyncio.sleep(2)  # 等待2秒
   result = await click_element("#button")
   ```

2. **使用更具体的选择器**：
   ```python
   # 不好：太宽泛
   await click_element("button")
   
   # 更好：更具体
   await click_element("#submit-button")
   await click_element("button[type='submit']")
   ```

3. **尝试不同选择器类型**：
   ```python
   # CSS选择器
   await click_element("#button")
   
   # XPath选择器
   await click_element("//button[@id='button']", selector_type="xpath")
   
   # 文本匹配
   await click_element("提交", selector_type="text")
   ```

### Q: 点击元素没有反应？

**A:** 可能的原因和解决方案：

1. **元素被遮挡**：
   ```python
   # 滚动到元素位置
   await execute_javascript(
       "document.querySelector('#button').scrollIntoView();"
   )
   await click_element("#button")
   ```

2. **需要等待元素可点击**：
   ```python
   # 检查元素是否可见
   result = await find_elements("#button")
   if result.get("elements"):
       await click_element("#button")
   ```

3. **使用 JavaScript 点击**：
   ```python
   await execute_javascript(
       "document.querySelector('#button').click();"
   )
   ```

### Q: 输入文本时出现乱码？

**A:** 检查编码设置：

```python
# 确保文本是正确的编码
text = "中文测试".encode('utf-8').decode('utf-8')
result = await input_text("#input", text)

# 或者先清空再输入
result = await input_text("#input", text, clear_first=True)
```

## 截图和文件

### Q: 截图文件太大怎么办？

**A:** 优化截图设置：

```python
# 使用 JPEG 格式（更小）
result = await get_screenshot_data(format="jpeg")

# 只截取可视区域
result = await take_screenshot(full_page=False)

# 截取特定元素
result = await take_screenshot(element_selector=".content")
```

### Q: 截图保存路径如何自定义？

**A:** 设置环境变量：

```bash
# 设置截图目录
export DRISSIONPAGE_MCP_SCREENSHOT_PATH="/custom/path/screenshots"

# 或在代码中指定文件名
result = await take_screenshot(filename="/custom/path/my_screenshot.png")
```

### Q: 如何批量处理截图？

**A:** 使用循环和异步处理：

```python
import asyncio

async def batch_screenshots(urls):
    for i, url in enumerate(urls):
        await navigate(url)
        await take_screenshot(filename=f"screenshot_{i}.png")
        await asyncio.sleep(1)  # 避免过快请求
```

## 网络和性能

### Q: 网络监控没有数据？

**A:** 确保正确启用监控：

```python
# 1. 先启用网络监控
result = await enable_network_monitoring()

# 2. 然后进行页面操作
result = await navigate("https://example.com")

# 3. 获取网络日志
logs = await get_network_logs()
```

### Q: 服务响应很慢怎么办？

**A:** 性能优化建议：

1. **启用缓存**：
   ```python
   result = await click_element("#button", use_cache=True)
   ```

2. **减少截图频率**：
   ```python
   # 只在必要时截图
   if need_screenshot:
       await take_screenshot()
   ```

3. **限制 DOM 深度**：
   ```python
   result = await get_dom_tree(max_depth=5)
   ```

4. **关闭不需要的标签页**：
   ```python
   # 定期清理标签页
   await close_unused_tabs()
   ```

### Q: 内存使用过高？

**A:** 内存优化策略：

```python
# 1. 定期清理截图文件
import os
import glob

def cleanup_screenshots():
    files = glob.glob("screenshots/*.png")
    for file in files[:-10]:  # 保留最新10个
        os.remove(file)

# 2. 限制网络日志数量
result = await get_network_logs(limit=50)

# 3. 使用无头模式
result = await connect_browser(headless=True)
```

## 开发和调试

### Q: 如何启用调试模式？

**A:** 设置详细日志：

```bash
# 启动时设置日志级别
drissionpage-mcp --log-level DEBUG

# 或设置环境变量
export DRISSIONPAGE_MCP_LOG_LEVEL=DEBUG
drissionpage-mcp
```

### Q: 如何调试 JavaScript 代码？

**A:** 使用浏览器开发者工具：

```python
# 1. 在代码中添加断点
code = """
console.log('调试信息');
debugger;  // 浏览器会在此处暂停
return document.title;
"""
result = await execute_javascript(code)

# 2. 或者使用 console.log 输出
code = "console.log('变量值:', someVariable);"
result = await execute_javascript(code)
```

### Q: 如何编写自定义工具？

**A:** 参考现有工具实现：

```python
from mcp.server.models import Tool
from mcp.types import TextContent

@server.tool()
async def custom_tool(
    param1: str,
    param2: int = 10
) -> list[TextContent]:
    """自定义工具描述"""
    try:
        # 工具逻辑实现
        result = f"处理结果: {param1}, {param2}"
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]
```

### Q: 如何处理并发请求？

**A:** 使用连接池和队列：

```python
import asyncio
from asyncio import Semaphore

# 限制并发数
semaphore = Semaphore(5)

async def handle_request(request):
    async with semaphore:
        # 处理请求
        result = await process_request(request)
        return result
```

### Q: 生产环境监控建议？

**A:** 监控关键指标：

```python
# 1. 健康检查端点
async def health_check():
    try:
        # 检查浏览器连接
        status = await get_browser_status()
        return {"status": "healthy", "browser": status}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# 2. 性能指标收集
import time

async def monitor_performance():
    start_time = time.time()
    # 执行操作
    result = await some_operation()
    duration = time.time() - start_time
    
    # 记录指标
    logger.info(f"操作耗时: {duration:.2f}秒")
    return result
```

## 故障排除

### Q: 服务无法启动？

**A:** 检查以下项目：

1. **Python 版本**：确保使用 Python 3.8+
2. **依赖安装**：`pip install -e .`
3. **权限问题**：确保有执行权限
4. **端口冲突**：检查 9222 端口是否被占用

### Q: 操作超时怎么办？

**A:** 调整超时设置：

```bash
# 增加超时时间
export DRISSIONPAGE_MCP_TIMEOUT=60

# 或在代码中处理
try:
    result = await click_element("#button")
except TimeoutError:
    # 重试或降级处理
    result = await fallback_operation()
```

### Q: 如何报告 Bug？

**A:** 提供以下信息：

1. **环境信息**：
   - 操作系统版本
   - Python 版本
   - Chrome 版本
   - 项目版本

2. **错误日志**：
   ```bash
   drissionpage-mcp --log-level DEBUG > debug.log 2>&1
   ```

3. **重现步骤**：
   - 详细的操作步骤
   - 预期结果 vs 实际结果
   - 最小化的重现代码

4. **在 GitHub 提交 Issue**：
   https://github.com/persist-1/DrissionPage-MCP-Server/issues

## 更多帮助

如果以上 FAQ 没有解决您的问题，可以通过以下方式获取帮助：

- 📖 **查看文档**：[在线文档](https://persist-1.github.io/DrissionPage-MCP-Server/)
- 🐛 **报告问题**：[GitHub Issues](https://github.com/persist-1/DrissionPage-MCP-Server/issues)
- 💬 **讨论交流**：[GitHub Discussions](https://github.com/persist-1/DrissionPage-MCP-Server/discussions)
- 📧 **联系作者**：通过 GitHub 私信

---

**提示**：本 FAQ 会持续更新，建议收藏此页面以获取最新信息。