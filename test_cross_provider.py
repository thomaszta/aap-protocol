#!/usr/bin/env python3
"""
AAP 跨 Provider 通信测试脚本 (使用已有账号)

测试 Molten <-> Fiction 之间的 Agent 能否互相发送消息。
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sdk/python'))

import aap
from aap import AAPClient
import requests


def print_result(name: str, success: bool, message: str = ""):
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if message:
        print(f"   {message}")


def test_fixed_accounts():
    """使用固定账号测试跨 Provider 通信"""
    
    # 账号信息
    AGENT_A = {
        "address": "ai:minibot~novel#openclaw.ai",
        "api_key": "829e89be-1d58-41d1-9d7b-3af68d5f1d46",
        "provider": "fiction.molten.it.com"
    }
    
    AGENT_B = {
        "address": "ai:thomaszta~main#www.molten.it.com",
        "api_key": "bc41aa10321244cb91c32fb874358005a9f72384cdcc4068",
        "provider": "www.molten.it.com"
    }
    
    print("\n" + "="*60)
    print("AAP 跨 Provider 通信测试")
    print("="*60)
    print(f"Agent A: {AGENT_A['address']} ({AGENT_A['provider']})")
    print(f"Agent B: {AGENT_B['address']} ({AGENT_B['provider']})")
    print("="*60 + "\n")
    
    client = AAPClient(timeout=30)
    
    # ========== 测试 1: Agent A (Fiction) -> Agent B (Molten) ==========
    print("📝 测试 1: Fiction -> Molten")
    
    try:
        result = client.send_message(
            from_addr=AGENT_A["address"],
            to_addr=AGENT_B["address"],
            content="Hello from Fiction to Molten!",
            message_type="private"
        )
        print_result("发送消息 A -> B", True, f"消息ID: {result.get('message_id')}")
    except Exception as e:
        print_result("发送消息 A -> B", False, str(e))
        return False
    
    # 获取 B 的消息
    import time
    time.sleep(1)
    
    try:
        messages = client.fetch_inbox(
            address=AGENT_B["address"],
            api_key=AGENT_B["api_key"],
            limit=10
        )
        
        found = False
        for msg in messages:
            content = msg.get("payload", {}).get("content", "")
            if "Fiction to Molten" in content:
                found = True
                print_result("接收消息 B", True, f"内容: {content}")
                break
        
        if not found:
            print_result("接收消息 B", False, "未找到测试消息")
            return False
    except Exception as e:
        print_result("接收消息 B", False, str(e))
        return False
    
    # ========== 测试 2: Agent B (Molten) -> Agent A (Fiction) ==========
    print("\n📝 测试 2: Molten -> Fiction")
    
    try:
        result = client.send_message(
            from_addr=AGENT_B["address"],
            to_addr=AGENT_A["address"],
            content="Hello from Molten to Fiction!",
            message_type="private"
        )
        print_result("发送消息 B -> A", True, f"消息ID: {result.get('message_id')}")
    except Exception as e:
        print_result("发送消息 B -> A", False, str(e))
        return False
    
    # 获取 A 的消息
    time.sleep(1)
    
    try:
        messages = client.fetch_inbox(
            address=AGENT_A["address"],
            api_key=AGENT_A["api_key"],
            limit=10
        )
        
        found = False
        for msg in messages:
            content = msg.get("payload", {}).get("content", "")
            if "Molten to Fiction" in content:
                found = True
                print_result("接收消息 A", True, f"内容: {content}")
                break
        
        if not found:
            print_result("接收消息 A", False, "未找到测试消息")
            return False
    except Exception as e:
        print_result("接收消息 A", False, str(e))
        return False
    
    # ========== 完成 ==========
    print("\n" + "="*60)
    print("🎉 跨 Provider 通信测试通过！")
    print("="*60)
    print(f"✅ Fiction ({AGENT_A['address']}) <-> Molten ({AGENT_B['address']})")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = test_fixed_accounts()
    sys.exit(0 if success else 1)
