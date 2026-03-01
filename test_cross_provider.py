#!/usr/bin/env python3
"""
AAP 跨 Provider 通信测试脚本

测试两个不同 Provider 之间的 Agent 能否互相发送消息。

用法:
    python test_cross_provider.py

环境变量:
    PROVIDER_A_URL: 第一个 Provider 的基础 URL
    PROVIDER_B_URL: 第二个 Provider 的基础 URL
"""

import os
import sys
import json

# 添加 SDK 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sdk/python'))

import aap
from aap import AAPClient


def print_result(name: str, success: bool, message: str = ""):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if message:
        print(f"   {message}")


def test_cross_provider(provider_a_url: str, provider_b_url: str):
    """测试跨 Provider 通信"""
    
    print("\n" + "="*60)
    print("AAP 跨 Provider 通信测试")
    print("="*60)
    print(f"Provider A: {provider_a_url}")
    print(f"Provider B: {provider_b_url}")
    print("="*60 + "\n")
    
    # 创建客户端
    client = AAPClient(verify_ssl=False, timeout=30)
    
    # ========== 步骤 1: 在 Provider A 注册 Agent A ==========
    print("📝 步骤 1: 在 Provider A 注册 Agent A...")
    
    try:
        import requests
        reg_url = f"{provider_a_url}/api/agent/register"
        reg_data = {
            "aap_address": f"ai:test-agent-a~test#{provider_a_url.replace('https://', '').replace('http://', '')}",
            "model": "test-model"
        }
        resp = requests.post(reg_url, json=reg_data, timeout=10)
        resp.raise_for_status()
        result_a = resp.json()
        
        agent_a_address = result_a["aap_address"]
        api_key_a = result_a["api_key"]
        
        print_result("在 Provider A 注册 Agent A", True, f"地址: {agent_a_address}")
        
    except Exception as e:
        print_result("在 Provider A 注册 Agent A", False, str(e))
        return False
    
    # ========== 步骤 2: 在 Provider B 注册 Agent B ==========
    print("\n📝 步骤 2: 在 Provider B 注册 Agent B...")
    
    try:
        reg_url = f"{provider_b_url}/api/agent/register"
        reg_data = {
            "aap_address": f"ai:test-agent-b~test#{provider_b_url.replace('https://', '').replace('http://', '')}",
            "model": "test-model"
        }
        resp = requests.post(reg_url, json=reg_data, timeout=10)
        resp.raise_for_status()
        result_b = resp.json()
        
        agent_b_address = result_b["aap_address"]
        api_key_b = result_b["api_key"]
        
        print_result("在 Provider B 注册 Agent B", True, f"地址: {agent_b_address}")
        
    except Exception as e:
        print_result("在 Provider B 注册 Agent B", False, str(e))
        return False
    
    # ========== 步骤 3: 从 Provider A 发送消息到 Provider B ==========
    print("\n📝 步骤 3: 从 Provider A 发送消息到 Provider B...")
    
    try:
        message_content = "Hello from cross-provider test!"
        
        result = client.send_message(
            from_addr=agent_a_address,
            to_addr=agent_b_address,
            content=message_content,
            message_type="private"
        )
        
        print_result("发送跨 Provider 消息", True, f"消息ID: {result.get('message_id')}")
        
    except Exception as e:
        print_result("发送跨 Provider 消息", False, str(e))
        return False
    
    # ========== 步骤 4: 在 Provider B 获取消息 ==========
    print("\n📝 步骤 4: 在 Provider B 获取消息...")
    
    try:
        import time
        time.sleep(1)  # 等待消息处理
        
        messages = client.fetch_inbox(
            address=agent_b_address,
            api_key=api_key_b,
            limit=10
        )
        
        # 查找我们发送的消息
        found = False
        for msg in messages:
            content = msg.get("payload", {}).get("content", "")
            if content == message_content:
                found = True
                print_result("接收跨 Provider 消息", True, f"内容: {content[:50]}...")
                break
        
        if not found:
            print_result("接收跨 Provider 消息", False, "消息未找到")
            print(f"   实际消息: {messages}")
            return False
        
    except Exception as e:
        print_result("接收跨 Provider 消息", False, str(e))
        return False
    
    # ========== 步骤 5: 反向测试 - Provider B 发给 Provider A ==========
    print("\n📝 步骤 5: 从 Provider B 发送消息到 Provider A...")
    
    try:
        message_content = "Reply from Provider B!"
        
        # 使用 Provider B 的地址发送
        result = client.send_message(
            from_addr=agent_b_address,
            to_addr=agent_a_address,
            content=message_content,
            message_type="private"
        )
        
        print_result("反向发送跨 Provider 消息", True, f"消息ID: {result.get('message_id')}")
        
    except Exception as e:
        print_result("反向发送跨 Provider 消息", False, str(e))
        return False
    
    # ========== 步骤 6: 验证反向消息 ==========
    print("\n📝 步骤 6: 验证反向消息...")
    
    try:
        messages_a = client.fetch_inbox(
            address=agent_a_address,
            api_key=api_key_a,
            limit=10
        )
        
        found = False
        for msg in messages_a:
            content = msg.get("payload", {}).get("content", "")
            if content == message_content:
                found = True
                print_result("接收反向消息", True, f"内容: {content}")
                break
        
        if not found:
            print_result("接收反向消息", False, "消息未找到")
            return False
        
    except Exception as e:
        print_result("接收反向消息", False, str(e))
        return False
    
    # ========== 完成 ==========
    print("\n" + "="*60)
    print("🎉 所有测试通过！跨 Provider 通信验证成功！")
    print("="*60)
    
    return True


def main():
    """主函数"""
    
    # 获取 Provider URL
    provider_a = os.environ.get("PROVIDER_A_URL", "http://localhost:5002")
    provider_b = os.environ.get("PROVIDER_B_URL", "http://localhost:5003")
    
    print(f"使用环境变量:")
    print(f"  PROVIDER_A_URL: {provider_a}")
    print(f"  PROVIDER_B_URL: {provider_b}")
    
    success = test_cross_provider(provider_a, provider_b)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
