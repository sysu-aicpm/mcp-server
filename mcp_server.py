#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP服务器 - 智能家居设备控制接口
这个服务器允许大模型通过MCP协议访问智能家居后端API，控制和查询设备信息。
"""

import os
import json
import argparse
import requests
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from pydantic import Field, BaseModel
from typing import Annotated, Literal

# 创建MCP服务器实例
mcp = FastMCP(name="智能家居设备控制中心")

# 定义参数模型
class ControlDeviceParams(BaseModel):
    """设备控制参数模型"""
    action: str = Field(..., description="要执行的操作，如 'set_temperature', 'switch' 等")
    parameters: Dict[str, Any] = Field(..., description="操作参数，根据不同设备类型和操作有所不同")

# 全局变量
backend_url = "http://localhost:8000"  # 默认后端地址
auth_token = ""  # 默认为空，需要用户提供

# 设备文档数据
def get_device_docs() -> Dict[str, Any]:
    """提供设备类型和控制方法的详细文档"""
    return {
        "device_types": {
            "air_conditioner": {
                "description": "空调设备",
                "control_commands": [
                    {
                        "action": "set_temperature",
                        "params": {
                            "temperature": "设置温度值，通常在16-30°C之间"
                        },
                        "example": {
                            "action": "set_temperature",
                            "params": {
                                "temperature": 24
                            }
                        }
                    },
                    {
                        "action": "switch",
                        "params": {
                            "state": "开关状态，'on'或'off'"
                        },
                        "example": {
                            "action": "switch",
                            "params": {
                                "state": "on"
                            }
                        }
                    }
                ]
            },
            "refrigerator": {
                "description": "冰箱设备",
                "control_commands": [
                    {
                        "action": "set_temperature",
                        "params": {
                            "temperature": "设置冰箱温度，范围：-20到10°C"
                        },
                        "example": {
                            "action": "set_temperature",
                            "params": {
                                "temperature": 4
                            }
                        }
                    },
                    {
                        "action": "switch",
                        "params": {
                            "state": "开关状态，'on'或'off'"
                        },
                        "example": {
                            "action": "switch",
                            "params": {
                                "state": "on"
                            }
                        }
                    }
                ]
            },
            "light": {
                "description": "灯具设备",
                "control_commands": [
                    {
                        "action": "set_brightness",
                        "params": {
                            "brightness": "亮度值，范围：0-100"
                        },
                        "example": {
                            "action": "set_brightness",
                            "params": {
                                "brightness": 80
                            }
                        }
                    },
                    {
                        "action": "switch",
                        "params": {
                            "state": "开关状态，'on'或'off'"
                        },
                        "example": {
                            "action": "switch",
                            "params": {
                                "state": "on"
                            }
                        }
                    }
                ]
            },
            "lock": {
                "description": "门锁设备",
                "control_commands": [
                    {
                        "action": "set_lock",
                        "params": {
                            "state": "锁定状态，'lock'或'unlock'"
                        },
                        "example": {
                            "action": "set_lock",
                            "params": {
                                "state": "lock"
                            }
                        }
                    }
                ]
            },
            "camera": {
                "description": "摄像头设备",
                "control_commands": [
                    {
                        "action": "set_recording",
                        "params": {
                            "state": "录制状态，'start'或'stop'"
                        },
                        "example": {
                            "action": "set_recording",
                            "params": {
                                "state": "start"
                            }
                        }
                    },
                    {
                        "action": "set_resolution",
                        "params": {
                            "resolution": "分辨率，'720p', '1080p'或'4k'"
                        },
                        "example": {
                            "action": "set_resolution",
                            "params": {
                                "resolution": "1080p"
                            }
                        }
                    }
                ]
            }
        },
        "device_status": {
            "online": "设备在线正常工作",
            "offline": "设备离线",
            "error": "设备出现错误"
        }
    }

# 获取当前配置信息
@mcp.tool
def get_config() -> Dict[str, Any]:
    """
    获取当前配置信息
    
    返回当前配置的后端API地址。认证令牌不会返回明文。
    """
    return {
        "success": True,
        "config": {
            "backend_address": backend_url,
            "auth_token_configured": bool(auth_token)
        }
    }

# 获取设备概览
@mcp.tool
def get_device_overview() -> Dict[str, Any]:
    """
    获取所有设备的概览信息
    
    此工具返回系统中所有设备的基本信息列表，包括设备ID、名称、状态等。
    在使用前，请确保服务器启动时已提供正确的认证令牌。
    """
    if not auth_token:
        return {"success": False, "message": "未配置认证令牌，请确保启动服务器时提供了--token参数"}
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{backend_url}/api/v1/devices/overview/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "success": False, 
            "message": f"获取设备概览失败: {str(e)}",
            "error_details": str(e)
        }

# 获取设备详情
@mcp.tool
def get_device_detail(
    device_id: Annotated[str, Field(description="设备ID，用于标识特定设备")]
) -> Dict[str, Any]:
    """
    获取特定设备的详细信息
    
    此工具返回指定设备的详细信息，包括设备状态、功耗、运行时间、日志等。
    在使用前，请确保服务器启动时已提供正确的认证令牌。
    """
    if not auth_token:
        return {"success": False, "message": "未配置认证令牌，请确保启动服务器时提供了--token参数"}
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{backend_url}/api/v1/devices/{device_id}/detail/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "success": False, 
            "message": f"获取设备详情失败: {str(e)}",
            "error_details": str(e)
        }

# 控制设备
@mcp.tool
def control_device(
    device_id: Annotated[str, Field(description="设备ID，用于标识要控制的设备")],
    action: Annotated[str, Field(description="要执行的操作，如'set_temperature'、'switch'等")],
    parameters: Annotated[Dict[str, Any], Field(description="操作参数，根据不同操作类型提供相应的参数")]
) -> Dict[str, Any]:
    """
    控制特定设备执行操作
    
    此工具用于向指定设备发送控制命令，执行特定操作。
    在使用前，请确保服务器启动时已提供正确的认证令牌。
    
    各设备支持的控制命令:
    
    1. 冰箱 (refrigerator):
       - set_temperature: 设置温度
         参数: temperature (范围: -20到10°C)
         示例: control_device(device_id="8", action="set_temperature", parameters={"temperature": 4})
       - switch: 开关冰箱
         参数: state ("on"或"off")
         示例: control_device(device_id="8", action="switch", parameters={"state": "on"})
    
    2. 灯 (light):
       - set_brightness: 设置亮度
         参数: brightness (范围: 0-100)
         示例: control_device(device_id="12", action="set_brightness", parameters={"brightness": 80})
       - switch: 开关灯
         参数: state ("on"或"off")
         示例: control_device(device_id="12", action="switch", parameters={"state": "on"})
    
    3. 门锁 (lock):
       - set_lock: 设置锁状态
         参数: state ("lock"或"unlock")
         示例: control_device(device_id="15", action="set_lock", parameters={"state": "lock"})
    
    4. 摄像头 (camera):
       - set_recording: 控制录制
         参数: state ("start"或"stop")
         示例: control_device(device_id="20", action="set_recording", parameters={"state": "start"})
       - set_resolution: 设置分辨率
         参数: resolution ("720p", "1080p"或"4k")
         示例: control_device(device_id="20", action="set_resolution", parameters={"resolution": "1080p"})
    
    5. 空调 (air_conditioner):
       - set_temperature: 设置温度
         参数: temperature (范围: 16-30°C)
         示例: control_device(device_id="5", action="set_temperature", parameters={"temperature": 24})
       - switch: 开关空调
         参数: state ("on"或"off")
         示例: control_device(device_id="5", action="switch", parameters={"state": "on"})
    """
    if not auth_token:
        return {"success": False, "message": "未配置认证令牌，请确保启动服务器时提供了--token参数"}
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "action": action,
        "parameters": parameters
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/v1/devices/{device_id}/control/", 
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "success": False, 
            "message": f"设备控制失败: {str(e)}",
            "error_details": str(e)
        }

# 获取设备类型文档
@mcp.tool
def get_device_type_docs(
    device_type: Annotated[
        Literal["air_conditioner", "refrigerator", "light", "lock", "camera"],
        Field(description="设备类型，指定要获取文档的设备类型")
    ] = None
) -> Dict[str, Any]:
    """
    获取设备控制文档
    
    此工具返回设备控制的详细文档，包括设备类型、支持的操作和参数说明。
    如果指定了设备类型，则返回该类型的详细控制文档；否则返回所有设备类型的概览。
    
    支持的设备类型:
    
    1. 冰箱 (refrigerator):
       - 支持设置温度 (set_temperature)，温度范围: -20到10°C
       - 支持开关控制 (switch)，状态: "on"或"off"
    
    2. 灯 (light):
       - 支持设置亮度 (set_brightness)，亮度范围: 0-100
       - 支持开关控制 (switch)，状态: "on"或"off"
    
    3. 门锁 (lock):
       - 支持设置锁状态 (set_lock)，状态: "lock"或"unlock"
    
    4. 摄像头 (camera):
       - 支持控制录制 (set_recording)，状态: "start"或"stop"
       - 支持设置分辨率 (set_resolution)，选项: "720p", "1080p"或"4k"
    
    5. 空调 (air_conditioner):
       - 支持设置温度 (set_temperature)，温度范围: 16-30°C
       - 支持开关控制 (switch)，状态: "on"或"off"
    
    设备状态说明:
    - online: 设备在线正常工作
    - offline: 设备离线
    - error: 设备出现错误
    """
    docs = get_device_docs()
    
    if device_type:
        if device_type in docs["device_types"]:
            return {
                "success": True,
                "device_type": device_type,
                "documentation": docs["device_types"][device_type]
            }
        else:
            return {
                "success": False,
                "message": f"未找到设备类型 '{device_type}' 的文档",
                "available_types": list(docs["device_types"].keys())
            }
    else:
        return {
            "success": True,
            "message": "设备类型文档概览",
            "available_types": list(docs["device_types"].keys()),
            "documentation": docs
        }

# 主函数
def main():
    parser = argparse.ArgumentParser(description="智能家居设备控制MCP服务器")
    parser.add_argument("--backend", default="http://localhost:8000", help="后端API地址")
    parser.add_argument("--token", default="", help="认证令牌")
    args = parser.parse_args()
    
    global backend_url, auth_token
    backend_url = args.backend
    auth_token = args.token
    
    print(f"启动MCP服务器，后端地址: {backend_url}")
    mcp.run()

if __name__ == "__main__":
    main()
