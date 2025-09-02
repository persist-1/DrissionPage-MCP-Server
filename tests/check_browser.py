#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""浏览器环境检查脚本 - 零依赖本地运行"""

import os
import sys
from DrissionPage import Chromium, ChromiumOptions

def check_browser_installation():
    """检查浏览器安装情况"""
    print("=== DrissionPage 浏览器环境检查 ===")
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 检查浏览器路径（便携版优先）
    browsers = {
        '便携版Chrome': [
            os.path.join(project_root, 'browsers', 'chrome-portable', 'chrome.exe'),
            os.path.join(project_root, 'browsers', 'chrome-portable', 'GoogleChromePortable.exe'),
        ],
        'Chrome': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME', '')),
        ],
        'Edge': [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        ]
    }
    
    found_browsers = []
    for browser_name, paths in browsers.items():
        for path in paths:
            if os.path.exists(path):
                found_browsers.append((browser_name, path))
                print(f"✅ 找到 {browser_name}: {path}")
                break
    
    if not found_browsers:
        print("❌ 未找到任何Chromium内核浏览器")
        print("\n📥 解决方案:")
        print("1. 下载便携版Chrome到 browsers/chrome-portable/ 目录")
        print("2. 或安装系统版Chrome: https://www.google.com/chrome/")
        print("3. 或使用系统自带的Edge浏览器")
        return False
    
    # 尝试配置第一个找到的浏览器
    browser_name, browser_path = found_browsers[0]
    try:
        ChromiumOptions().set_browser_path(browser_path).save()
        print(f"✅ 已配置 {browser_name} 为默认浏览器")
        if '便携版' in browser_name:
            print("🎉 使用项目内置便携版Chrome，无需额外安装!")
    except Exception as e:
        print(f"❌ 配置浏览器失败: {e}")
        return False
    
    # 测试浏览器连接
    try:
        print("🔄 测试浏览器连接...")
        co = ChromiumOptions()
        co.set_local_port(9222)
        co.headless(True)  # 使用无头模式测试
        
        browser = Chromium(co)
        tab = browser.latest_tab
        tab.get('about:blank')  # 访问空白页测试
        print(f"✅ 浏览器连接成功")
        browser.quit()
        return True
    except Exception as e:
        print(f"❌ 浏览器连接失败: {e}")
        print("可能的原因:")
        print("  1. 端口9222被占用")
        print("  2. 浏览器权限不足")
        print("  3. 防火墙阻止连接")
        return False

def manual_setup():
    """手动配置浏览器路径"""
    print("\n=== 手动配置浏览器路径 ===")
    print("请输入浏览器可执行文件的完整路径:")
    print("例如: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    
    while True:
        path = input("浏览器路径: ").strip().strip('"')
        if not path:
            print("路径不能为空")
            continue
            
        if not os.path.exists(path):
            print(f"文件不存在: {path}")
            continue
            
        try:
            ChromiumOptions().set_browser_path(path).save()
            print(f"✅ 浏览器路径已保存: {path}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

def get_browser_version_info():
    """获取浏览器版本信息"""
    print("\n=== 浏览器版本信息获取 ===")
    print("请在浏览器地址栏输入以下地址查看版本信息:")
    print("Chrome: chrome://version")
    print("Edge: edge://version")
    print("建议使用版本100以上的浏览器")

def main():
    """主函数"""
    print("DrissionPage MCP 浏览器环境配置工具")
    print("=" * 50)
    
    # 自动检查
    if check_browser_installation():
        print("\n🎉 浏览器环境配置完成!")
        print("现在可以正常使用DrissionPage MCP服务了")
        return True
    
    # 手动配置选项
    print("\n自动配置失败，请选择操作:")
    print("1. 手动指定浏览器路径")
    print("2. 查看浏览器版本信息获取方法")
    print("3. 退出")
    
    while True:
        choice = input("请选择 (1-3): ").strip()
        
        if choice == '1':
            if manual_setup():
                print("\n请重新运行此脚本验证配置")
            break
        elif choice == '2':
            get_browser_version_info()
            break
        elif choice == '3':
            print("退出配置")
            break
        else:
            print("无效选择，请输入1-3")
    
    return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        sys.exit(1)