# 检查并拉取 python:3.10-slim 镜像
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q '^python:3.10-slim$'; then
  echo "python:3.10-slim not found, pulling..."
  docker pull python:3.10-slim
else
  echo "python:3.10-slim already exists."
fi

# 检查并拉取 node:18 镜像
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q '^node:18$'; then
  echo "node:18 not found, pulling..."
  docker pull node:18
else
  echo "node:18 already exists."
fi

# 检查并拉取 nginx:alpine 镜像
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q '^nginx:alpine$'; then
  echo "nginx:alpine not found, pulling..."
  docker pull nginx:alpine
else
  echo "nginx:alpine already exists."
fi

docker-compose up --build