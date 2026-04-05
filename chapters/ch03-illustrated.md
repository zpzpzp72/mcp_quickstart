# 第3章：本地 MCP Server 5分钟上手——以 OpenClaw 为例

> **📍 章节定位**：全教程的核心动手环节
> **⏱ 预计耗时**：5–10 分钟
> **🎯 目标**：跑通第一个 MCP Server，产生"我做到了"的正反馈

---

## 🔖 本章路线图

```
Step 1  环境确认        →  确认 OpenClaw + Python 已就绪
Step 2  安装 MCP SDK    →  pip install mcp
Step 3  写 10 行代码    →  weather_server.py
Step 4  配置到 OpenClaw →  mcp.config.json
Step 5  验证连通性      →  问 AI："成都天气怎么样？"
```

---

## Step 1：环境确认

在开始之前，先确认你的环境满足基本要求。打开终端，执行以下命令：

```bash
# 检查 OpenClaw 版本（需支持 MCP）
openclaw --version

# 检查 Python 版本（需 3.10+）
python3 --version
```

**期望输出示例：**

```
$ openclaw --version
OpenClaw v2026.3.24

$ python3 --version
Python 3.12.0
```

> **⚠️ 如果 OpenClaw 版本过低**
> 升级方法：`openclaw update`
> 或参考第5章「升级注意事项」
>
> **⚠️ 如果 Python 版本低于 3.10**
> 推荐使用 [uv](https://github.com/astral-sh/uv) 管理多版本：
> `uv python install 3.12 && uv python list`

---

## Step 2：安装 MCP SDK

MCP 提供了 Python 和 TypeScript 两套 SDK。本教程使用 Python 版本，因为：

- ✅ Python 生态丰富（数据处理、API 调用）
- ✅ 安装简单：`pip install mcp`
- ✅ ZP 熟悉的语言

```bash
# 推荐：使用 uv（更快）
uv add mcp

# 或者：pip（通用）
pip install mcp
```

**✅ 验证安装成功：**

```bash
python3 -c "import mcp; print(f'MCP SDK v{mcp.__version__}')"
```

**期望输出：**

```
MCP SDK v1.26.0
```

---

## Step 3：编写第一个 MCP Server（10行代码）

这是整个教程的核心——你将亲手写一个**天气查询 MCP Server**。

### 3.1 新建项目目录

```bash
cd ~  # 或任意你喜欢的目录
git clone https://github.com/zpzpzp72/mcp_quickstart.git
cd mcp_quickstart
```

### 3.2 创建天气服务代码

新建文件 `weather_server.py`，内容如下：

```python
#!/usr/bin/env python3
"""
Weather MCP Server - 简单天气查询示例
接收城市名 → 返回模拟天气数据
"""

import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent

# 服务器实例
server = Server("weather-server", version="1.0.0")

# 模拟天气数据（生产环境请替换为真实API）
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
```

### 3.3 代码结构解析

```
┌─────────────────────────────────────────────────────────┐
│  weather_server.py 整体架构                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Server 实例                                            │
│  ┌──────────────────────────────────────────────┐      │
│  │  server = Server("weather-server", v="1.0.0") │      │
│  └──────────────────────────────────────────────┘      │
│         │                                               │
│         ├── @server.list_tools()                       │
│         │      定义工具列表（get_weather）              │
│         │                                               │
│         └── @server.call_tool()                        │
│                处理工具调用 → 返回 JSON                  │
│                                                         │
│  async def main()                                       │
│  └── await serve(server)  ← stdio 通信                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.4 关键片段说明

**片段 1：Server 创建**
```python
from mcp.server import Server
server = Server("weather-server", version="1.0.0")
```
→ 创建一个名为 `weather-server` 的 MCP Server，版本 1.0.0

**片段 2：工具定义（最重要）**
```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="查询指定城市的天气信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"],  # city 是必填参数
            },
        )
    ]
```
→ 告诉 AI："我有一个叫 `get_weather` 的工具，它需要一个 `city` 参数"

**片段 3：工具处理**
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        city = arguments.get("city", "")
        # ... 查询逻辑 ...
        return [TextContent(type="text", text=json.dumps(result))]
```
→ 当 AI 调用 `get_weather` 时，执行这段代码并返回结果

### 3.5 验证语法

```bash
python3 -c "import ast; ast.parse(open('weather_server.py').read()); print('✅ 语法正确')"
```

**期望输出：**

```
✅ 语法正确
```

---

## Step 4：配置到 OpenClaw

MCP Server 写好了，但 OpenClaw 怎么知道它在哪里？这就需要配置。

### 4.1 找到配置文件

OpenClaw 的 MCP 配置通常在：

| 路径 | 适用场景 |
|------|---------|
| `~/.openclaw/mcp.config.json` | 全局配置（所有项目生效） |
| `./mcp.config.json` | 项目级配置 |

本教程使用项目级配置（方便分享 Demo）。

### 4.2 编辑 mcp.config.json

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/home/zhiping/mcp_quickstart/weather_server.py"]
    }
  }
}
```

> **⚠️ 路径注意**
> 使用**绝对路径**，不要用 `~` 或相对路径
> 正确：`/home/zhiping/mcp_quickstart/weather_server.py`
> 错误：`~/mcp_quickstart/weather_server.py`

### 4.3 配置文件解析

```
mcpServers: {
  weather: {               ← Server 名称（AI 调用时用）
    command: "python",     ← 启动命令
    args: ["路径"]         ← Server 脚本路径
  }
}
```

---

## Step 5：验证连通性

### 5.1 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

### 5.2 测试调用

在 OpenClaw 对话中输入：

```
查询成都今天的天气
```

**期望返回（JSON 格式）：**

```json
{
  "city": "成都",
  "temperature": "20°C",
  "condition": "阴",
  "humidity": "72%",
  "wind": "北风2级",
  "tips": "建议带伞出行"
}
```

### 5.3 成功标志

如果你看到了上面的 JSON 返回，说明：

```
✅ MCP Server 已注册成功
✅ AI 能够调用工具
✅ 数据正确返回
```

---

## 🖼 截图验证点（关键步骤）

以下是验证连通性时的关键截图说明：

| 截图位置 | 应该看到 |
|---------|---------|
| OpenClaw 对话输入框 | "查询成都今天的天气" |
| AI 返回内容 | JSON 格式天气数据 |
| Terminal（MCP Server） | "🌤️ Weather MCP Server 已启动" |

---

## ❓ 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| AI 不返回天气数据 | Server 未启动 | 检查 `python weather_server.py` 是否报错 |
| 路径找不到 | 使用了相对路径 | 改用绝对路径 |
| 返回空结果 | city 参数未传递 | 检查 `arguments.get("city")` 是否正确 |
| 端口被占用 | 已有同名校服务 | 换一个名字，如 `weather_v2` |

---

## 📝 本章小结

```
✅ 学会了 MCP Server 的 3 个核心组件：
   1. Server 实例
   2. list_tools() — 声明有哪些工具
   3. call_tool() — 处理工具调用逻辑

✅ 掌握了 OpenClaw MCP 配置方法
✅ 验证了端到端连通性
```

**下一步**：继续第4章 → 构建 AI 盯盘助手（A股行情 + 邮件告警）

---

*第3章完成度：60%（代码✅ 配置✅ 验证待手动确认）*
