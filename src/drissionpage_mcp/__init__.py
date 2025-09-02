# -*- coding: utf-8 -*-
"""DrissionPage MCP Server - 浏览器自动化MCP服务器

基于DrissionPage和FastMCP的浏览器自动化MCP服务器，提供丰富的浏览器操作API供AI调用。
"""

__version__ = "0.2.0"
__author__ = "DrissionPageMCP Team"
__description__ = "DrissionPage MCP Server for browser automation"

from .main import DrissionPageMCP

__all__ = ["DrissionPageMCP"]