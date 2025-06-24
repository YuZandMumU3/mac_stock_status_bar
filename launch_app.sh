#!/bin/bash
# macOS状态栏应用启动脚本

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 股票监控状态栏应用"
echo "工作目录: $(pwd)"

# 检查是否已有实例在运行
if pgrep -f "status_bar_app.py" > /dev/null; then
    echo "⚠️  应用程序已在运行"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "⚙️  首次运行，请先配置股票信息..."
    python3 configure.py
    echo ""
fi

# 在后台启动应用程序
echo "📊 启动股票监控应用..."
nohup python3 "$SCRIPT_DIR/status_bar_app.py" --daemon >> "$SCRIPT_DIR/app.log" 2>&1 &

echo "✅ 应用程序已在后台启动"
echo "💡 使用以下命令停止应用："
echo "   ./stop_app.sh"
