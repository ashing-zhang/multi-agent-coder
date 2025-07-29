import socket

def test_dns_resolution():
    try:
        # 尝试解析一个常见的域名
        socket.getaddrinfo('www.google.com', 80)
        print('DNS resolution successful')
    except socket.gaierror as e:
        print(f'DNS resolution failed: {e}')

def test_network_connection():
    try:
        # 尝试连接到一个常见的服务器
        sock = socket.create_connection(('www.google.com', 80), timeout=5)
        sock.close()
        print('Network connection successful')
    except socket.gaierror as e:
        print(f'Network connection failed: {e}')
    except socket.timeout as e:
        print(f'Network connection timed out: {e}')

if __name__ == '__main__':
    test_dns_resolution()
    test_network_connection()