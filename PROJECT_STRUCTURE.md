# 项目结构

```
mac_status_bar/
├── README.md                   # 项目说明文档
├── configure.py                # 🔧 配置入口（推荐使用）
├── config.json                 # 配置文件
├── requirements.txt            # 依赖列表
├── launch_app.sh              # 启动脚本
├── stop_app.sh                # 停止脚本
│
├── status_bar_app.py          # 📱 应用入口
├── status_bar_controller.py   # 🎮 应用控制器
├── config_manager.py          # ⚙️ 配置管理器
│
├── docs/                      # 📚 文档目录
│   ├── PROJECT_OVERVIEW.md    # 项目概览
│   └── QUICK_START.md         # 快速开始
│
├── tools/                     # 🔧 配置工具
│   ├── config.py              # 配置查看工具
│   ├── quick_config.py        # 快捷配置工具
│   └── config_gui.py          # 图形配置工具
│
├── data_providers/            # 📊 数据提供者
│   ├── __init__.py
│   ├── base_provider.py       # 基础提供者
│   ├── provider_factory.py    # 提供者工厂
│   ├── stock_provider.py      # 股票数据提供者
│   ├── system_provider.py     # 系统信息提供者
│   ├── network_provider.py    # 网络信息提供者
│   └── weather_provider.py    # 天气信息提供者
│
├── ui/                        # 🖥️ 用户界面
│   ├── __init__.py
│   └── status_bar_ui.py       # 状态栏UI管理
│
└── utils/                     # 🛠️ 工具类
    ├── __init__.py
    ├── icon_manager.py        # 图标管理
    └── thread_manager.py      # 线程管理
```

## 🚀 快速开始

1. **配置股票**: `python3 configure.py`
2. **启动应用**: `python3 status_bar_app.py`

## 📝 主要文件说明

### 核心文件
- `status_bar_app.py` - 应用程序入口点
- `status_bar_controller.py` - 核心业务逻辑控制器
- `config_manager.py` - 配置文件管理和热重载
- `configure.py` - 统一配置入口，提供多种配置方式选择

### 配置工具
- `tools/quick_config.py` - 命令行快捷配置（推荐）
- `tools/config_gui.py` - 图形化配置界面
- `tools/config.py` - 配置文件查看和编辑

### 数据层
- `data_providers/stock_provider.py` - 股票数据获取和处理
- `data_providers/provider_factory.py` - 数据提供者工厂模式
- `data_providers/base_provider.py` - 数据提供者基类

### 界面层
- `ui/status_bar_ui.py` - macOS状态栏界面管理
- `utils/icon_manager.py` - 状态栏图标管理

## 🎯 使用建议

1. **首次使用**: 运行 `python3 configure.py` 选择快捷配置
2. **日常使用**: 使用 `./launch_app.sh` 启动应用
3. **修改配置**: 右键状态栏图标选择重新加载配置
4. **问题排查**: 查看 `app.log` 日志文件 