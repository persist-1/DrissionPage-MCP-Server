
## 便携版Chrome路径配置
**在'src/drissionpage_mcp/core/browser_manager.py'中已经配置Chrome内核浏览器的路径**

但请考虑以下几种状态来判断是否需要进行额外配置：

- 如果你的电脑安装了Chrome内核的浏览器（如Edge、Chrome），并且是默认安装，则无需配置

- 如果你的电脑安装了Chrome内核的浏览器，但不是默认安装，则需要配置路径

- 如果你的电脑没有安装Chrome内核的浏览器，但又不想下载安装，则'browsers/'中提供了便捷版Chrome浏览器安装包以使用，注意安装路径为'browsers/chrome-portable/'