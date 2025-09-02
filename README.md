<div align="center">

<img src="./docs/site_config/public/images/logo.png" alt="DrissionPage-MCP-Server Logo" width="200">

# DrissionPage-MCP-Server

基于 DrissionPage 的模型上下文协议 (MCP) 服务，为 AI 助手提供强大的浏览器自动化能力。

[![GitHub stars](https://img.shields.io/github/stars/persist-1/DrissionPage-MCP-Server?style=social)](https://github.com/persist-1/DrissionPage-MCP-Server/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/persist-1/DrissionPage-MCP-Server?style=social)](https://github.com/persist-1/DrissionPage-MCP-Server/network/members)
[![GitHub issues](https://img.shields.io/github/issues/persist-1/DrissionPage-MCP-Server)](https://github.com/persist-1/DrissionPage-MCP-Server/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/persist-1/DrissionPage-MCP-Server)](https://github.com/persist-1/DrissionPage-MCP-Server/pulls)
[![GitHub license](https://img.shields.io/github/license/persist-1/DrissionPage-MCP-Server)](https://github.com/persist-1/DrissionPage-MCP-Server/blob/main/LICENSE)

</div>

## ✨ 核心特性

🌐 **浏览器自动化** - 页面导航、元素操作、截图等完整功能  
🔧 **MCP协议支持** - 与AI助手无缝集成的标准化接口  
📸 **截图与DOM** - 页面分析、元素定位、结构获取  
🚀 **异步高性能** - 基于FastMCP框架的高效服务  
🛠️ **17工具集** - 涵盖浏览器管理到文件处理的全方位功能

## 🚀 快速开始

### 安装
```bash
# 克隆项目
git clone https://github.com/persist-1/DrissionPage-MCP-Server.git
cd DrissionPage-MCP-Server/

# 使用 uv 同步环境
uv sync
```

### 启动服务
```bash
# 启动MCP服务（STDIO模式）
drissionpage-mcp
```

### 在AI助手中配置
在 Trae AI IDE 中添加 MCP 服务配置：
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
![MCP配置效果](docs/site_config/public/images/mcp配置效果(Trae%20ide).png)

## 📱 使用案例

### 网页自动化操作
<div align="center">
  <img src="docs/site_config/public/images/用例测试1.png" alt="用例测试1" width="45%">
  <img src="docs/site_config/public/images/用例测试2.png" alt="用例测试2" width="45%">
</div>

### 复杂页面交互
<div align="center">
  <img src="docs/site_config/public/images/用例测试3_1.png" alt="用例测试3_1" width="30%">
  <img src="docs/site_config/public/images/用例测试3_2.png" alt="用例测试3_2" width="30%">
  <img src="docs/site_config/public/images/用例测试3_3.png" alt="用例测试3_3" width="30%">
</div>

### 基本使用示例
```python
# 连接浏览器
result = await connect_browser(port=9222, headless=False)

# 导航并截图
result = await navigate("https://example.com")
result = await take_screenshot("page.png")

# 元素操作
result = await click_element("#submit-button")
result = await input_text("#username", "your_username")
```

## 🛠️ MCP 工具列表

| 分类 | 工具 | 功能描述 |
|------|------|----------|
| 🌐 **浏览器管理** | 1.`connect_browser` | 连接/启动浏览器 |
| | 2.`new_tab` | 创建新标签页 |
| | 3.`navigate` | 页面导航 |
| 🎯 **元素操作** | 4.`click_element` | 点击元素 |
| | 5.`input_text` | 输入文本 |
| | 6.`get_element_text` | 获取元素文本内容 |
| | 7.`get_page_text` | 获取页面完整文本内容 |
| 📸 **截图功能** | 8.`take_screenshot` | 页面/元素截图 |
| | 9.`get_screenshot_data` | 获取截图数据 |
| 🌳 **DOM操作** | 10.`get_dom_tree` | 获取DOM树结构 |
| | 11.`find_elements` | 查找页面元素 |
| 🔍 **网络监控** | 12.`enable_network_monitoring` | 启用网络监控 |
| | 13.`get_network_logs` | 获取网络日志 |
| 📁 **文件操作** | 14.`save_page_source` | 保存页面源码 |
| | 15.`get_cookies` | 获取Cookies |
| ⚡ **高级功能** | 16.`execute_javascript` | 执行JavaScript |
| | 17.`run_cdp_command` | 执行CDP命令 |

## ⚙️ 环境配置

```bash
# 基本配置
export DRISSIONPAGE_MCP_LOG_LEVEL=INFO
export DRISSIONPAGE_MCP_HEADLESS=false
export DRISSIONPAGE_MCP_TIMEOUT=30

# 路径配置（可选）
export DRISSIONPAGE_MCP_BROWSER_PATH=/path/to/chrome
export DRISSIONPAGE_MCP_DOWNLOAD_PATH=/path/to/downloads
export DRISSIONPAGE_MCP_SCREENSHOT_PATH=/path/to/screenshots
```

## 🏗️ 项目架构

```
DrissionPage-MCP-Server/
├── .github/                    # GitHub 配置
│   ├── ISSUE_TEMPLATE/         # Issue 模板
│   └── workflows/              # GitHub Actions 工作流
│       └── deploy.yml          # 自动部署配置
├── browsers/                   # 浏览器相关文件
│   ├── chrome-portable/        # 便携版 Chrome（可选）
│   └── readme_please.md        # 浏览器使用说明
├── docs/                       # 文档目录
│   ├── site_config/            # VitePress 文档站点
│   │   ├── .vitepress/         # VitePress 配置
│   │   ├── public/             # 静态资源（图片等）
│   │   ├── *.md               # 各类文档文件
│   │   └── index.md           # 文档首页
│   ├── package.json           # 文档站点依赖
│   └── ds_run_dev.bat         # 开发脚本
├── src/                        # 源代码目录
│   └── drissionpage_mcp/       # 主要代码包
│       ├── config/             # 配置模块
│       │   └── settings.py     # 环境配置和设置
│       ├── core/               # 核心功能模块
│       │   ├── browser_manager.py    # 浏览器管理
│       │   ├── element_handler.py    # 元素操作处理
│       │   ├── file_handler.py       # 文件操作处理
│       │   └── network_listener.py   # 网络监听
│       ├── services/           # 服务层
│       │   ├── cdp_service.py        # Chrome DevTools 协议服务
│       │   ├── dom_service.py        # DOM 操作服务
│       │   └── screenshot_service.py # 截图服务
│       ├── utils/              # 工具模块
│       │   ├── helpers.py            # 辅助函数
│       │   └── text_matcher.py      # 文本匹配工具
│       └── main.py             # MCP 服务入口
├── tests/                      # 测试目录
│   ├── integration/            # 集成测试
│   ├── check_browser.py        # 浏览器检查脚本
│   └── local_build_test.ps1    # 本地构建测试
├── pyproject.toml              # Python 项目配置
├── requirements*.txt           # Python 依赖文件
├── pytest.ini                 # 测试配置
└── uv.lock                     # UV 锁定文件
```

### 核心模块说明

- **core/**: 核心业务逻辑，包含浏览器管理、元素操作、文件处理等
- **services/**: 服务层，提供 CDP、DOM、截图等专业服务
- **config/**: 配置管理，处理环境变量和系统设置
- **utils/**: 通用工具，提供辅助函数和文本处理能力

## 📚 文档

- 📖 **[在线文档](https://persist-1.github.io/DrissionPage-MCP-Server/)** - 完整的项目文档
- 🚀 **[使用说明](docs/site_config/instruction.md)** - 快速上手指南
- 🏗️ **[开发指南](docs/site_config/development-guide.md)** - 开发环境配置
- 🔧 **[项目架构](docs/site_config/architecture.md)** - 架构设计说明
- 📋 **[API参考](docs/site_config/api-reference.md)** - 详细API文档

## 🔧 故障排除

| 问题 | 解决方案 |
|------|----------|
| 🌐 浏览器连接失败 | 确保Chrome已安装，检查调试端口配置 |
| 🎯 元素找不到 | 检查选择器，等待页面加载，使用更具体选择器 |
| 📸 截图失败 | 检查磁盘空间、文件权限、截图目录 |
| 🔍 网络监控无数据 | 确保已启用监控，检查过滤条件 |

```bash
# 启用调试日志
drissionpage-mcp --log-level DEBUG
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目 → 2. 创建分支 → 3. 提交更改 → 4. 推送分支 → 5. 创建 PR

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">
  <strong>⭐ 如果这个项目对你有帮助，请给个 Star！</strong>
</div>