# DrissionPage MCP Server

基于 DrissionPage 的模型上下文协议 (MCP) 服务器，提供强大的浏览器自动化和网页操作功能。

## 功能特性

### 🚀 核心功能
- **浏览器管理**: 连接/启动浏览器，管理标签页，页面导航
- **元素操作**: 点击、输入、获取文本、滚动等交互操作
- **网络监控**: 监听网络请求，过滤响应数据
- **截图服务**: 页面截图、元素截图、全页面截图
- **DOM操作**: 获取DOM树结构，查找元素，解析页面内容
- **文件处理**: 保存页面源码，下载文件，管理Cookies
- **JavaScript执行**: 运行自定义JavaScript代码
- **CDP协议**: 直接执行Chrome DevTools Protocol命令

### 🏗️ 架构特点
- **模块化设计**: 分层架构，职责清晰
- **异步支持**: 基于FastMCP框架，支持异步操作
- **类型安全**: 完整的类型注解和验证
- **配置灵活**: 丰富的配置选项和环境变量支持
- **错误处理**: 完善的异常处理和日志记录

## 快速开始

### 安装依赖

```bash
# 安装项目依赖
pip install -e .

# 或安装开发依赖
pip install -e ".[dev]"
```

### 启动服务器

```bash
# 使用默认配置启动（STDIO模式）
drissionpage-mcp

# 设置日志级别
drissionpage-mcp --log-level DEBUG
```

**注意**: 本MCP服务器运行在STDIO模式下，主要用于与AI助手集成，不支持HTTP服务器模式。

### 基本使用

1. **连接浏览器**
```python
# 连接到现有浏览器或启动新浏览器
result = await connect_browser(port=9222, headless=False)
```

2. **页面导航**
```python
# 导航到指定URL
result = await navigate("https://example.com")
```

3. **元素操作**
```python
# 点击元素
result = await click_element("#submit-button")

# 输入文本
result = await input_text("#username", "your_username")

# 获取元素文本
text = await get_element_text(".title")
```

4. **截图**
```python
# 截取页面截图
result = await take_screenshot("page.png")

# 截取元素截图
result = await take_screenshot("element.png", element_selector=".content")
```

5. **DOM操作**
```python
# 获取DOM树
dom_tree = await get_dom_tree("body", max_depth=5)

# 查找元素
elements = await find_elements(".item")
```

## 项目结构

```
REFINE/
├── src/drissionpage_mcp/          # 源代码目录
│   ├── __init__.py               # 包初始化
│   ├── main.py                   # 主入口模块
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── browser_manager.py    # 浏览器管理
│   │   ├── element_handler.py    # 元素操作
│   │   ├── network_listener.py   # 网络监听
│   │   └── file_handler.py       # 文件处理
│   ├── services/                 # 业务服务模块
│   │   ├── __init__.py
│   │   ├── dom_service.py        # DOM服务
│   │   ├── screenshot_service.py # 截图服务
│   │   └── cdp_service.py        # CDP服务
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   └── helpers.py            # 辅助函数
│   └── config/                   # 配置管理
│       ├── __init__.py
│       └── settings.py           # 配置设置
├── tests/                        # 测试目录
├── docs/                         # 文档目录
├── agent_zone/                   # 项目管理文档
├── pyproject.toml               # 项目配置
└── README.md                    # 项目说明
```

## 配置说明

### 环境变量

```bash
# 日志级别
export DRISSIONPAGE_MCP_LOG_LEVEL=INFO

# 浏览器路径
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

### 配置文件

项目使用 `config/settings.py` 中的 `DEFAULT_CONFIG` 作为默认配置，支持以下配置项：

- **browser**: 浏览器相关配置
- **screenshot**: 截图相关配置
- **network**: 网络监控配置
- **dom**: DOM操作配置
- **file**: 文件处理配置
- **logging**: 日志配置
- **performance**: 性能配置

## 开发指南

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd drissionpage-mcp/REFINE

# 安装开发依赖
pip install -e ".[dev]"

# 安装预提交钩子
pre-commit install
```

### 代码规范

项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **Flake8**: 代码检查
- **MyPy**: 类型检查
- **Pytest**: 单元测试

```bash
# 格式化代码
black src/ tests/

# 排序导入
isort src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/

# 运行测试
pytest tests/
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_browser_manager.py

# 运行测试并生成覆盖率报告
pytest --cov=drissionpage_mcp --cov-report=html

# 运行特定标记的测试
pytest -m "not slow"  # 跳过慢速测试
pytest -m "unit"      # 只运行单元测试
```

## API 文档

### MCP 工具列表

#### 浏览器管理
- `connect_browser`: 连接浏览器
- `new_tab`: 创建新标签页
- `navigate`: 页面导航

#### 元素操作
- `click_element`: 点击元素
- `input_text`: 输入文本
- `get_element_text`: 获取元素文本
- `get_page_text`: 获取页面文本

#### 截图功能
- `take_screenshot`: 截取截图
- `get_screenshot_data`: 获取截图数据

#### DOM操作
- `get_dom_tree`: 获取DOM树
- `find_elements`: 查找元素

#### 网络监控
- `enable_network_monitoring`: 启用网络监控
- `get_network_logs`: 获取网络日志

#### 文件操作
- `save_page_source`: 保存页面源码
- `get_cookies`: 获取Cookies

#### JavaScript和CDP
- `execute_javascript`: 执行JavaScript
- `run_cdp_command`: 执行CDP命令

### MCP 资源列表

- `config://default`: 获取默认配置
- `instructions://all`: 获取所有工具指令
- `status://browser`: 获取浏览器状态

## 故障排除

### 常见问题

1. **浏览器连接失败**
   - 确保Chrome浏览器已安装
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

4. **网络监控无数据**
   - 确保已启用网络监控
   - 检查过滤条件是否正确
   - 验证页面是否有网络请求

### 日志调试

```bash
# 启用详细日志
drissionpage-mcp --log-level DEBUG

# 查看日志文件
tail -f logs/drissionpage_mcp.log
```

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)