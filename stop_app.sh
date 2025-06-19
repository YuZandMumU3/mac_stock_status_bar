#!/bin/bash
# macOS状态栏应用停止脚本

echo "正在停止状态栏应用..."

# 查找并停止所有相关进程
pkill -f "status_bar_app.py"

# 等待进程停止
sleep 2

# 检查是否还有进程在运行
if pgrep -f "status_bar_app.py" > /dev/null; then
    echo "强制停止应用程序..."
    pkill -9 -f "status_bar_app.py"
else
    echo "✅ 应用程序已停止"
fi
