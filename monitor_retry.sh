#!/bin/bash
# Monitor the continuous retry script

echo "========================================"
echo "🧙 Veo 3.1 Retry Monitor"
echo "========================================"
echo ""

# Check if script is running
if pgrep -f "continuous_retry.py" > /dev/null; then
    echo "✅ Continuous retry script is RUNNING"
    echo ""

    # Show last 20 lines of log
    echo "📋 Recent Activity:"
    echo "----------------------------------------"
    tail -n 20 continuous_retry.log
    echo "----------------------------------------"
    echo ""
    echo "💡 To see live updates: tail -f continuous_retry.log"
    echo "💡 To stop the script: pkill -f continuous_retry.py"
else
    echo "❌ Continuous retry script is NOT running"
    echo ""
    echo "To start it:"
    echo "  ./venv/bin/python3 continuous_retry.py 2>&1 | tee continuous_retry.log &"
fi

echo ""
echo "========================================"
