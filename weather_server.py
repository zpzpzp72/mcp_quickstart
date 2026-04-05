#!/usr/bin/env python3
"""
Weather MCP Server - 简单天气查询示例
接收城市名 → 返回模拟天气数据

依赖: pip install mcp
运行: python weather_server.py
配置: 写入 ~/.openclaw/mcp.config.json
"""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent

# 服务器实例
server = Server("weather-server", version="1.0.0")

# 模拟天气数据 (生产环境请替换为真实API)
WEATHER_DATA = {
    "北京": {"temp": 18, "condition": "晴", "humidity": 45, "wind": "北风3级"},
    "上海": {"temp": 22, "condition": "多云", "humidity": 65, "wind": "东风2级"},
    "成都": {"temp": 20, "condition": "阴", "humidity": 72, "wind": "北风2级"},
    "深圳": {"temp": 26, "condition": "晴", "humidity": 55, "wind": "南风3级"},
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="get_weather",
            description="查询指定城市的天气信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如：北京、上海、成都",
                    }
                },
                "required": ["city"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    if name == "get_weather":
        city = arguments.get("city", "")
        
        # 模拟天气查询
        if city in WEATHER_DATA:
            data = WEATHER_DATA[city]
            result = {
                "city": city,
                "temperature": f"{data['temp']}°C",
                "condition": data["condition"],
                "humidity": f"{data['humidity']}%",
                "wind": data["wind"],
                "tips": _get_weather_tips(data["condition"], data["temp"]),
            }
        else:
            # 未知城市，返回默认
            result = {
                "city": city,
                "temperature": "25°C",
                "condition": "晴",
                "humidity": "50%",
                "wind": "微风",
                "tips": "天气数据获取中，请稍后...",
            }
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    
    raise ValueError(f"Unknown tool: {name}")


def _get_weather_tips(condition: str, temp: int) -> str:
    """根据天气状况生成建议"""
    tips = []
    if condition == "晴":
        tips.append("适合户外活动")
    elif condition == "阴":
        tips.append("建议带伞出行")
    elif condition == "雨":
        tips.append("记得带雨具")
    
    if temp < 10:
        tips.append("注意保暖")
    elif temp > 28:
        tips.append("注意防暑")
    
    return "；".join(tips) if tips else "今日天气良好"


async def main():
    """运行服务器（stdio模式）"""
    from mcp.server.stdio import serve
    
    print("🌤️  Weather MCP Server 已启动", file=__import__('sys').stderr)
    await serve(server)


if __name__ == "__main__":
    asyncio.run(main())
