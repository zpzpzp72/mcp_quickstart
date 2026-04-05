# mcp_quickstart

 MCP 快速入门模板 — 用 Python 写一个天气查询 Server

---

## 🚀 5分钟快速开始

### Step 1：安装依赖

```bash
pip install mcp
```

### Step 2：运行天气 Server

```bash
python weather_server.py
```

服务通过 **stdio** 通信，启动后保持运行即可。

### Step 3：配置到 OpenClaw

编辑 `~/.openclaw/mcp.config.json`（或项目内 `mcp.config.json`）：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/weather_server.py"]
    }
  }
}
```

> 💡 路径用绝对路径，如 `/home/zhiping/mcp_quickstart/weather_server.py`

### Step 4：重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

### Step 5：验证

在 OpenClaw 对话中尝试：

```
查询成都天气
```

**期望输出：**
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

---

## 📁 项目结构

```
mcp_quickstart/
├── README.md           # 本文件
├── mcp.config.json     # MCP 配置（OpenClaw 格式）
└── weather_server.py   # 天气查询示例 Server
```

---

## 🔧 核心代码解析

### Server 创建

```python
from mcp.server import Server
server = Server("weather-server", version="1.0.0")
```

### 工具定义（list_tools）

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
                "required": ["city"]
            }
        )
    ]
```

### 工具处理（call_tool）

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        city = arguments.get("city", "")
        # ... 查询逻辑
        return [TextContent(type="text", text=json.dumps(result))]
```

### 启动服务（stdio）

```python
async def main():
    from mcp.server.stdio import serve
    await serve(server)
```

---

## 📚 更多资源

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Model Context Protocol 官方文档](https://modelcontextprotocol.io)
- [OpenClaw MCP 配置](https://github.com/openclaw/openclaw)

---

*祝你玩得开心！*
