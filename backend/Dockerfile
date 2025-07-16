FROM python:3.10-slim

WORKDIR /app

# 保证安装系统安全补丁
RUN apt-get update && apt-get upgrade -y && apt-get clean

COPY backend/requirements.txt ./requirements.txt

# 安装 requirements.txt 文件中列出的所有 Python 依赖包，并且不使用 pip 的缓存以减少镜像体积
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY backend/ ./backend/
# 这样，backend 容器内会有 /app/frontend_dist 目录
COPY frontend/src ./frontend_dist
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
