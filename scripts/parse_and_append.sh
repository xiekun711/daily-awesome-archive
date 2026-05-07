#!/bin/bash
# ======================================================
# github-awesome-daily - parse daily push and append to data dir
# Usage: ./scripts/parse_and_append.sh <YYYYMMDD>
# If no date given, uses today
# ======================================================
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$PROJECT_DIR/data"

DATE="${1:-$(date +%Y%m%d)}"
SOURCE_FILE="/home/ubuntu/hermes-agent/scripts/github_daily_output_${DATE}.txt"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "Source file not found: $SOURCE_FILE"
    exit 1
fi

mkdir -p "$DATA_DIR"
OUTPUT_FILE="$DATA_DIR/$DATE.md"

echo "# GitHub Awesome Daily - $DATE" > "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Extract project lines from the source report
while IFS= read -r line; do
    # Match lines like: "- [owner/repo](https://github.com/...)"
    if echo "$line" | grep -q '\['; then
        if echo "$line" | grep -q 'https://github.com'; then
            echo "$line" >> "$OUTPUT_FILE"
        fi
    fi
done < "$SOURCE_FILE"

echo "" >> "$OUTPUT_FILE"
echo "Done: $OUTPUT_FILE"
echo "Project count: $(grep -c 'github.com' "$OUTPUT_FILE" 2>/dev/null || echo 0)"
