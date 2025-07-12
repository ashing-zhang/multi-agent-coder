#!/usr/bin/env python3
"""
测试脚本：验证所有agent API是否正常工作
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123"
}

def test_auth():
    """测试认证功能"""
    print("=== 测试认证功能 ===")
    
    # 注册用户
    print("1. 注册用户...")
    register_response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    if register_response.status_code == 200:
        print("✓ 用户注册成功")
    elif register_response.status_code == 400:
        print("✓ 用户已存在")
    else:
        print(f"✗ 注册失败: {register_response.status_code}")
        return None
    
    # 登录
    print("2. 用户登录...")
    login_response = requests.post(f"{BASE_URL}/auth/token", data=TEST_USER)
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("✓ 登录成功")
        return token
    else:
        print(f"✗ 登录失败: {login_response.status_code}")
        return None

def test_agent_api(agent_name, endpoint, test_data, token):
    """测试单个agent API"""
    print(f"\n=== 测试 {agent_name} API ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"发送请求到: {endpoint}")
        print(f"测试数据: {test_data}")
        
        response = requests.post(f"{BASE_URL}{endpoint}", 
                               json=test_data, 
                               headers=headers,
                               stream=True)
        
        if response.status_code == 200:
            print("✓ API调用成功，开始接收流式响应...")
            
            # 接收流式响应
            content = ""
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    content += chunk
                    print(f"收到数据块: {len(chunk)} 字符")
            
            print(f"✓ 流式响应完成，总长度: {len(content)} 字符")
            print(f"响应内容预览: {content[:200]}...")
            return True
        else:
            print(f"✗ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False

def test_agent_list(token):
    """测试agent列表API"""
    print("\n=== 测试Agent列表API ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/agent/list", headers=headers)
        
        if response.status_code == 200:
            agents = response.json()
            print("✓ Agent列表获取成功")
            print(f"可用Agents: {agents}")
            return True
        else:
            print(f"✗ Agent列表获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("开始测试Multi-Agent API...")
    
    # 1. 测试认证
    token = test_auth()
    if not token:
        print("认证失败，无法继续测试")
        return
    
    # 2. 测试agent列表
    test_agent_list(token)
    
    # 3. 测试各个agent API
    test_cases = [
        {
            "name": "需求分析Agent",
            "endpoint": "/requirements/stream",
            "data": {"description": "创建一个简单的计算器应用"}
        },
        {
            "name": "文档生成Agent", 
            "endpoint": "/agent/doc/stream",
            "data": {"requirement": "def add(a, b): return a + b"}
        },
        {
            "name": "代码生成Agent",
            "endpoint": "/agent/coder/stream", 
            "data": {"requirement": "创建一个Python函数来计算斐波那契数列"}
        },
        {
            "name": "代码审查Agent",
            "endpoint": "/agent/reviewer/stream",
            "data": {"requirement": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"}
        },
        {
            "name": "测试生成Agent",
            "endpoint": "/agent/test/stream",
            "data": {"requirement": "def add(a, b): return a + b"}
        },
        {
            "name": "代码整合Agent",
            "endpoint": "/agent/finalizer/stream",
            "data": {
                "requirement": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
                "suggestions": "建议使用迭代而不是递归来提高性能"
            }
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        if test_agent_api(test_case["name"], test_case["endpoint"], test_case["data"], token):
            success_count += 1
        time.sleep(1)  # 避免请求过于频繁
    
    # 4. 测试历史消息API
    print("\n=== 测试历史消息API ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/messages/", headers=headers)
        
        if response.status_code == 200:
            messages = response.json()
            print("✓ 历史消息获取成功")
            print(f"会话数量: {len(messages)}")
            return True
        else:
            print(f"✗ 历史消息获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 请求异常: {str(e)}")
        return False
    
    # 5. 输出测试结果
    print(f"\n=== 测试完成 ===")
    print(f"成功: {success_count}/{total_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")

if __name__ == "__main__":
    main() 