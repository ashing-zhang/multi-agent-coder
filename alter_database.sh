#!/bin/bash
# 用法: ./alter_database.sh "your migration message"

set -e

if [ -z "$1" ]; then
  echo "请提供本次迁移的描述信息，如：sh alter_database.sh 'add email to user'"
  exit 1
fi

MIGRATION_MSG="$1"

# 设置PYTHONPATH为当前目录，确保alembic能正确导入包
export PYTHONPATH=$(pwd)

# 生成迁移脚本
alembic revision --autogenerate -m "$MIGRATION_MSG"

# 执行数据库升级
alembic upgrade head

echo "数据库迁移已完成。" 