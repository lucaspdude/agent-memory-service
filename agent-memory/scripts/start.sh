#!/bin/bash
# Start the local Agent Memory Service

if [ ! -d "$HOME/.agent-memory" ]; then
    echo "❌ Not set up yet! Run ./scripts/setup.sh first"
    exit 1
fi

echo "🚀 Starting Agent Memory Service..."
echo "   URL: http://127.0.0.1:8742"
echo ""

source "$HOME/.agent-memory/venv/bin/activate"
export DB_PATH="$HOME/.agent-memory/data/memory.db"
cd "$HOME/.agent-memory/service"

exec uvicorn main:app --host 127.0.0.1 --port 8742 --log-level info
