#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
状态栏应用程序
Mac状态栏定制信息显示应用，支持股票价格、系统信息和其他自定义内容
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

def setup_environment():
    """设置运行环境"""
    # 添加当前目录到系统路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

def create_launch_script():
    """创建启动脚本，用于后台运行"""
    current_dir = Path(__file__).parent.absolute()
    script_path = current_dir / "launch_app.sh"
    
    script_content = f"""#!/bin/bash
# macOS状态栏应用启动脚本
# 此脚本将应用在后台运行，不依赖终端窗口

cd "{current_dir}"

# 检查是否已有实例在运行
if pgrep -f "status_bar_app.py" > /dev/null; then
    echo "应用程序已在运行"
    exit 1
fi

# 在后台启动应用程序
nohup python3 "{current_dir}/status_bar_app.py" --daemon > /dev/null 2>&1 &

echo "应用程序已在后台启动"
echo "使用以下命令停止应用："
echo "pkill -f status_bar_app.py"
"""
    
    # 写入启动脚本
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 启动脚本已创建: {script_path}")
    return script_path

def create_stop_script():
    """创建停止脚本"""
    current_dir = Path(__file__).parent.absolute()
    script_path = current_dir / "stop_app.sh"
    
    script_content = """#!/bin/bash
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
"""
    
    # 写入停止脚本
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 停止脚本已创建: {script_path}")
    return script_path

def run_foreground():
    """前台运行模式"""
    print("🚀 前台运行模式启动...")
    print("按 Ctrl+C 停止应用程序")
    
    setup_environment()
    from status_bar_controller import main
    main()

def run_daemon():
    """后台运行模式"""
    print("🚀 后台运行模式启动...")
    
    # 重定向标准输出和错误输出到日志文件
    current_dir = Path(__file__).parent.absolute()
    log_file = current_dir / "app.log"
    
    # 重定向输出到日志文件
    import sys
    sys.stdout = open(log_file, 'a', encoding='utf-8')
    sys.stderr = sys.stdout
    
    # 启动应用
    setup_environment()
    from status_bar_controller import main
    main()

def check_status():
    """检查应用程序运行状态"""
    try:
        result = subprocess.run(['pgrep', '-f', 'status_bar_app.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"✅ 应用程序正在运行 (PID: {', '.join(pids)})")
            return True
        else:
            print("❌ 应用程序未运行")
            return False
    except Exception as e:
        print(f"❌ 检查状态时出错: {e}")
        return False

def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description="macOS状态栏应用程序")
    parser.add_argument('--daemon', action='store_true', 
                       help='在后台运行（守护进程模式）')
    parser.add_argument('--create-scripts', action='store_true',
                       help='创建启动和停止脚本')
    parser.add_argument('--status', action='store_true',
                       help='检查应用程序运行状态')
    
    args = parser.parse_args()
    
    if args.create_scripts:
        launch_script = create_launch_script()
        stop_script = create_stop_script()
        print("\n使用方法:")
        print(f"  启动应用: ./{launch_script.name}")
        print(f"  停止应用: ./{stop_script.name}")
        print(f"  检查状态: python3 {__file__} --status")
        return
    
    if args.status:
        check_status()
        return
    
    if args.daemon:
        # 检查是否已有实例在运行
        if check_status():
            print("❌ 应用程序已在运行，请先停止现有实例")
            return
        run_daemon()
    else:
        run_foreground()

if __name__ == "__main__":
    main()
