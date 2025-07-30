# 系统配置文件

import os

class Settings:
    PROJECT_NAME = "Multi-Agent 协作平台"
    VERSION = "0.1.0"
    # DeepSeek API base URL
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    # 可扩展更多配置

settings = Settings()
