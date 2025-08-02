# 系统配置文件

import os

class Settings:
    PROJECT_NAME = "Multi-Agent 协作平台"
    VERSION = "0.1.0"
    # DeepSeek API base URL
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    
    # Kafka配置
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_REQUEST = os.getenv("KAFKA_TOPIC_REQUEST", "agent_request")
    KAFKA_TOPIC_RESPONSE = os.getenv("KAFKA_TOPIC_RESPONSE", "agent_response")

settings = Settings()
