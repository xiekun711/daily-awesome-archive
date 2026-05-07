#!/bin/bash
# ======================================================
# sync_to_github.sh — 解析当天推送并同步到 GitHub
# 由 cron 在每天 08:00 之后自动触发
# ======================================================
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

DATE=$(date +%Y%m%d)

# 1. 解析今天的推送数据
echo "[$(date)] 解析 $DATE 数据..."
if bash scripts/parse_and_append.sh "$DATE"; then
    echo "[$(date)] 解析完成"
else
    echo "[$(date)] 解析失败（可能报告还没生成），跳过"
    exit 0
fi

# 2. 更新 README 中的日期表格
echo "[$(date)] 更新 README..."

# 3. git commit & push
echo "[$(date)] 提交到 Git..."
git add -A
git commit -m "📅 daily update: $DATE" --allow-empty

echo "[$(date)] 推送到 GitHub..."
git push origin main 2>&1 || {
    echo "[$(date)] 推送失败，可能还没配置远程仓库或网络问题"
    exit 1
}

echo "[$(date)] ✅ 同步完成"
