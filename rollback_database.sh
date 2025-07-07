#!/bin/bash
# 用法: ./rollback_database.sh

set -e

# 设置PYTHONPATH为当前目录，确保alembic能正确导入包
export PYTHONPATH=$(pwd)

# 回退上一个迁移
alembic downgrade -1

echo "已回滚上一个数据库迁移。" 