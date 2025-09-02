# DrissionPage-MCP-Server 使用说明

- **项目在线文档地址** [https://persist-1.github.io/DrissionPage-MCP-Server/](https://persist-1.github.io/DrissionPage-MCP-Server/)
- **项目仓库地址** [https://github.com/persist-1/DrissionPage-MCP-Server](https://github.com/persist-1/DrissionPage-MCP-Server)

## 环境准备

### 系统要求
- Python 3.10+
- Chrome/Chromium 浏览器
- Windows 10/11

### 创建/配置/激活 Python 虚拟环境
```shell   
# 进入项目根目录
cd DrissionPage-MCP-Server

# 同步虚拟环境
uv sync

# Windows 激活虚拟环境
.venv\Scripts\activate
```


## 浏览器配置

本项目使用 DrissionPage 控制浏览器，支持以下方式：

1. **使用现有 Chrome 浏览器**（推荐）
   - 确保已安装 Chrome 浏览器
   - 项目会自动检测并使用系统 Chrome

2. **使用便携版 Chrome**
   - 项目提供了便携版 Chrome 安装包
   - 位于 `browsers/` 目录
   
## 启动 MCP 服务

### 基本启动
```shell
# 使用默认配置启动（STDIO模式）
drissionpage-mcp

# 设置日志级别
drissionpage-mcp --log-level DEBUG
```

### 配置说明

项目支持通过环境变量进行配置：

```shell
# 日志级别
export DRISSIONPAGE_MCP_LOG_LEVEL=INFO

# 浏览器路径（可选）
export DRISSIONPAGE_MCP_BROWSER_PATH=/path/to/chrome

# 下载目录
export DRISSIONPAGE_MCP_DOWNLOAD_PATH=/path/to/downloads

# 截图目录
export DRISSIONPAGE_MCP_SCREENSHOT_PATH=/path/to/screenshots

# 无头模式
export DRISSIONPAGE_MCP_HEADLESS=false

# 超时设置
export DRISSIONPAGE_MCP_TIMEOUT=30
```

## 在 AI 助手中使用

### Trae AI IDE 配置

1. 打开 Trae AI IDE 设置
2. 找到 MCP 服务配置
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

![MCP配置效果](./images/mcp配置效果(Trae ide).png)

### 基本使用示例

连接浏览器并进行基本操作：

```python
# 1. 连接浏览器
result = await connect_browser(port=9222, headless=False)

# 2. 导航到网页
result = await navigate("https://example.com")

# 3. 截图
result = await take_screenshot("page.png")

# 4. 查找元素
elements = await find_elements(".button")

# 5. 点击元素
result = await click_element("#submit")

# 6. 输入文本
result = await input_text("#username", "your_username")
```

## 使用案例展示

### 案例1：网页自动化操作

![用例测试1](/images/用例测试1.png)
![用例测试2](/images/用例测试2.png)

### 案例2：复杂页面交互

<div style="display: flex; gap: 10px; flex-wrap: wrap;">
  <img src="/images/用例测试3_1.png" alt="用例测试3_1" style="width: 32%; min-width: 200px;">
  <img src="/images/用例测试3_2.png" alt="用例测试3_2" style="width: 32%; min-width: 200px;">
  <img src="/images/用例测试3_3.png" alt="用例测试3_3" style="width: 32%; min-width: 200px;">
</div>

## 故障排除

### 常见问题

1. **浏览器连接失败**
   - 确保 Chrome 浏览器已安装
   - 检查浏览器是否正在运行
   - 验证浏览器调试端口配置

2. **元素找不到**
   - 检查选择器是否正确
   - 等待页面加载完成
   - 使用更具体的选择器

3. **截图失败**
   - 确保有足够的磁盘空间
   - 检查文件权限
   - 验证截图目录是否存在



## 免责声明
> **免责声明：**
> 
> 大家请以学习为目的使用本仓库，爬虫违法违规的案件：https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China  
>
>本项目的所有内容仅供学习和参考之用，禁止用于商业用途。任何人或组织不得将本仓库的内容用于非法用途或侵犯他人合法权益。本仓库所涉及的爬虫技术仅用于学习和研究，不得用于对其他平台进行大规模爬虫或其他非法行为。对于因使用本仓库内容而引起的任何法律责任，本仓库不承担任何责任。使用本仓库的内容即表示您同意本免责声明的所有条款和条件。

## 📸 项目展示

### 🔧 MCP 配置效果
<div align="center">
<img src="/images/mcp配置效果(Trae ide).png" alt="MCP配置效果" width="800">
</div>

*在 Trae AI IDE 中成功配置 DrissionPage-MCP-Server 的效果展示*