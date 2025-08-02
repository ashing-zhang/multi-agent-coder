import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import router as api_router
from dotenv import load_dotenv
from confluent_kafka import Producer, Consumer, KafkaException
from .core.config import settings
from .services.kafka_consumer_service import KafkaConsumerService
import threading

app = FastAPI(title="Multi-Agent 协作平台")

# Kafka配置
kafka_conf = {
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS
}

# 初始化Kafka生产者
producer = Producer(kafka_conf)

# 初始化Kafka消费者
consumer_conf = {
    'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'agent_group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(consumer_conf)
consumer.subscribe([settings.KAFKA_TOPIC_REQUEST])

# 启动Kafka消费者服务
kafka_consumer_service = KafkaConsumerService()
consumer_thread = threading.Thread(target=kafka_consumer_service.start_consuming)
consumer_thread.start()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)

dotenv_path = 'backend/.env'
print('dotenv_path:',dotenv_path)
load_dotenv(dotenv_path)
# 根据环境变量 ENV 判断前端静态目录
env = os.getenv('ENV', 'dev')
if env == 'dev':
    frontend_path = 'frontend/src'
else:
    frontend_path = 'frontend_dist'
print('frontend_path:',frontend_path)
# 将前端静态文件挂载到根路径 "/" 下。
# 使用 `StaticFiles` 类指定静态文件的目录为 `frontend_path`，该路径根据环境变量 ENV 动态确定。
# `html=True` 表示当访问目录时默认返回 index.html 文件，常用于单页应用（SPA）。
# `name="frontend"` 为该挂载点指定一个名称，方便后续引用。
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
