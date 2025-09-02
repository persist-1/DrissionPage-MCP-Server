import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

// https://vitepress.dev/reference/site-config
export default withMermaid(
  defineConfig({
  title: "DrissionPage-MCP-Server",
  description: "基于 DrissionPage 的模型上下文协议 (MCP) 服务，提供强大的浏览器自动化和网页操作功能。",
  base: '/DrissionPage-MCP-Server/',
  
  // 忽略死链接检查
  ignoreDeadLinks: true,

  // Markdown 配置
  markdown: {
    // 启用 mermaid 图表支持
    config: (md) => {
      // 可以在这里添加其他 markdown 插件配置
    }
  },

  head: [
      // 添加图标
      ['link', { rel: 'icon', type: 'image/svg+xml', href: '/images/logo.svg' }]
    ],

  themeConfig: {

    // logo: '/images/logo1.svg',
    siteTitle: 'DrissionPage-MCP-Server | 项目文档',

    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '项目文档', link: '/README' },
      { text: '使用说明', link: '/instruction' },
    ],

    sidebar: [
      {
        text: '快速开始',
        items: [
          { text: '使用说明', link: '/instruction' },
          { text: '项目概述', link: '/README' }
        ]
      },
      {
        text: '开发文档',
        items: [
          { text: '项目架构', link: '/architecture' },
          { text: 'MCP工具文档', link: '/mcp-tools' },
          { text: 'API参考', link: '/api-reference' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/persist-1/DrissionPage-MCP-Server' }
    ],

    // 站点页脚配置
    footer: {
      message: "Released under the MIT License",
      copyright: "Copyright © 2025-present persist-1",
    },
  }
})
)
