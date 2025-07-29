import subprocess
import time

def test_mcp_server():
    try:
        # 尝试启动MCP服务器
        process = subprocess.Popen(['npx', '-y', '@upstash/context7-mcp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # 等待一段时间以确保服务器启动
        time.sleep(10)
        # 检查进程是否仍在运行
        if process.poll() is None:
            print('MCP server started successfully')
            # 终止进程
            process.terminate()
        else:
            stdout, stderr = process.communicate()
            print(f'MCP server failed to start: {stderr.decode()}')
    except Exception as e:
        print(f'Failed to start MCP server: {e}')

if __name__ == '__main__':
    test_mcp_server()