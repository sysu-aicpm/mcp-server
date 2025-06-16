# 智能家居设备控制 MCP 服务器

这个 MCP 服务器允许大模型通过 Model Context Protocol (MCP) 协议访问智能家居后端 API，实现设备控制和信息查询功能。

## 功能特点

- 提供设备控制接口，支持各种智能家居设备的操作
- 查询设备概览和详细信息
- 内置丰富的设备文档，指导大模型正确使用各类设备
- 支持通过命令行参数配置后端 API 地址和认证令牌

## 支持的设备类型及控制参数

1. 空调 (air_conditioner):
   - 设置温度 (set_temperature)
     - 参数: temperature (范围: 16-30°C)
     - 示例: `control_device(device_id="5", action="set_temperature", parameters={"temperature": 24})`
   - 开关控制 (switch)
     - 参数: state ("on"或"off")
     - 示例: `control_device(device_id="5", action="switch", parameters={"state": "on"})`

2. 冰箱 (refrigerator):
   - 设置温度 (set_temperature)
     - 参数: temperature (范围: -20到10°C)
     - 示例: `control_device(device_id="8", action="set_temperature", parameters={"temperature": 4})`
   - 开关控制 (switch)
     - 参数: state ("on"或"off")
     - 示例: `control_device(device_id="8", action="switch", parameters={"state": "on"})`

3. 灯 (light):
   - 设置亮度 (set_brightness)
     - 参数: brightness (范围: 0-100)
     - 示例: `control_device(device_id="12", action="set_brightness", parameters={"brightness": 80})`
   - 开关控制 (switch)
     - 参数: state ("on"或"off")
     - 示例: `control_device(device_id="12", action="switch", parameters={"state": "on"})`

4. 门锁 (lock):
   - 设置锁状态 (set_lock)
     - 参数: state ("lock"或"unlock")
     - 示例: `control_device(device_id="15", action="set_lock", parameters={"state": "lock"})`

5. 摄像头 (camera):
   - 控制录制 (set_recording)
     - 参数: state ("start"或"stop")
     - 示例: `control_device(device_id="20", action="set_recording", parameters={"state": "start"})`
   - 设置分辨率 (set_resolution)
     - 参数: resolution ("720p", "1080p"或"4k")
     - 示例: `control_device(device_id="20", action="set_resolution", parameters={"resolution": "1080p"})`

## 设备状态说明

- online: 设备在线正常工作
- offline: 设备离线
- error: 设备出现错误

## 安装依赖

```bash
pip install fastmcp requests
```

## 使用方法

### 启动服务器

```bash
python mcp_server.py --backend http://backend-api-address:8000/api/v1 --token <your_auth_token>
```

your_auth_token 令牌需要在通过`POST /auth/login`登录到后端后获取

参数说明:
- `--backend`: 后端 API 地址，默认为 `http://localhost:8000`
- `--token`: 认证令牌，用于访问后端 API 的授权


### 对话测试

你可以使用 cursor 或者 cline(VSCode插件)与大模型对话，在其中调用MCP服务器。

```json
{
  "mcpServers": {
    "cpm-smarthome": {
      "disabled": false,
      "timeout": 60,
      "transportType": "stdio",
      "command": "python",
      "args": [
        "/path/to/mcp_server.py",
        "--token",
        "your_auth_token",
        "--backend",
        "http://backend-api-address:8000/api/v1"
      ]
    }
  }
}
```

### 可用工具

服务器提供以下工具供大模型使用:

1. `get_config()`: 获取当前配置信息
   - 返回后端 API 地址和认证令牌配置状态
   - 注意：认证令牌不会返回明文

2. `get_device_overview()`: 获取所有设备的概览信息
   - 返回系统中所有设备的基本信息列表
   - 包括设备ID、名称、状态等信息

3. `get_device_detail(device_id)`: 获取特定设备的详细信息
   - 返回指定设备的详细状态信息
   - 包括设备状态、功耗、运行时间、日志等

4. `control_device(device_id, action, parameters)`: 控制特定设备执行操作
   - 用于向指定设备发送控制命令
   - 具体参数请参考上方设备类型说明

5. `get_device_type_docs(device_type)`: 获取设备类型的控制文档
   - 不指定设备类型时返回所有设备类型的概览
   - 指定设备类型时返回该类型的详细控制文档

## 后端 API 接口

本服务器连接到以下后端 API 接口:

1. 控制设备: `POST /devices/{device_id}/control/`
2. 查询设备概要: `GET /devices/overview/`
3. 查询设备详情: `GET /devices/{device_id}/detail/`

## 注意事项

- 在使用任何工具前，请确保服务器启动时已提供正确的认证令牌
- 不同类型的设备支持不同的操作和参数，请参考设备文档了解详情
- 所有API调用都需要提供有效的认证令牌
- 设备控制操作会返回操作结果，请检查返回的 success 字段确认操作是否成功 