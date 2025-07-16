FROM nginx:alpine
# 设置工作目录为 nginx 默认的静态文件目录
WORKDIR /usr/share/nginx/html
# 拷贝所有 src 下静态资源（html/js/css/components/assets 等）
COPY frontend/src/ ./
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 