# macOS 股票监控状态栏应用

一个简洁高效的 macOS 状态栏应用，实时监控A股股票价格，支持颜色指示器、趋势图表和多种显示模式。

## ✨ 主要功能

- 🎯 **实时股票数据** - A股价格和涨跌幅实时更新
- 📊 **趋势图表** - 透明背景股票走势图，高质量显示
- 🎨 **颜色指示器** - 直观显示涨跌状态
  - 🔴📈 上涨：红色圆圈 + 上升图标
  - 🟢📉 下跌：绿色圆圈 + 下降图标  
  - ⚪️➡️ 平盘：灰色圆圈 + 横向箭头
- 🔄 **多种模式** - 单只显示/轮换显示/多只同显
- ⚡ **智能缓存** - 减少API请求，提升性能
- 🔧 **简易配置** - 多种配置方式，操作简单

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置股票
```bash
python3 configure.py
```
选择配置方式：
- **快捷配置** - 命令行界面，简单快速
- **图形配置** - 可视化界面，直观易用

### 3. 启动应用
```bash
python3 status_bar_app.py
```
或使用启动脚本：
```bash
./launch_app.sh
```

## 📊 趋势图表功能

### 图表特性
- **透明背景** - 完美融入系统状态栏
- **高质量渲染** - 160 DPI高清显示
- **智能缓存** - 自动管理图表文件
- **多种生成方式** - 支持Matplotlib和PIL

### 图表配置
```json
{
  "chart_settings": {
    "enabled": true,
    "width": 180,
    "height": 45,
    "cache_hours": 12,
    "max_cache_files": 30
  }
}
```

## 🎨 颜色功能

### 颜色指示器
| 状态 | 指示器 | 说明 |
|------|--------|------|
| 上涨 | 🔴📈 | 红色圆圈 + 上升趋势图 |
| 下跌 | 🟢📉 | 绿色圆圈 + 下降趋势图 |
| 平盘 | ⚪️➡️ | 灰色圆圈 + 横向箭头 |

### 显示效果
- **启用颜色**：🔴📈 贵州茅台 1426.0 (+2.15%)
- **禁用颜色**：贵州茅台 1426.0 (+2.15%)

## ⚙️ 配置选项

### 显示模式
- **单只股票** - 专注监控一只股票
- **轮换显示** - 多只股票自动切换
- **多只同显** - 同时显示多只股票

### 配置方式
```bash
# 主配置入口
python3 configure.py

# 快捷配置
python3 tools/quick_config.py

# 图形配置
python3 tools/config_gui.py
```

### 配置文件示例
```json
{
  "update_interval": 5,
  "display_format": "{colored_display}",
  "stock_info": {
    "enabled": true,
    "symbols": ["600519", "000001"],
    "use_color_indicators": true,
    "rotate_stocks": true,
    "rotate_interval": 10
  },
  "chart_settings": {
    "enabled": true,
    "width": 180,
    "height": 45
  }
}
```

## 📊 支持股票

- **A股主板** - 6位数字代码（如：600519 贵州茅台）
- **深市主板** - 0开头6位数字（如：000001 平安银行）
- **创业板** - 3开头6位数字（如：300015 爱尔眼科）

## 🔧 状态栏菜单

右键点击状态栏图标：
- 🔄 更新信息
- ⚙️ 重新加载配置
- 🔀 切换股票
- ✏️ 编辑显示格式
- 📝 编辑配置文件

## 🛠️ 故障排除

### 颜色不显示？
1. 确认配置中 `use_color_indicators` 为 `true`
2. 检查 `display_format` 使用 `{colored_display}`
3. 重新加载配置或重启应用

### 股票数据获取失败？
1. 检查网络连接
2. 确认股票代码格式正确（6位数字）
3. 查看日志：`tail -f app.log`

### 配置不生效？
1. 通过状态栏菜单"重新加载配置"
2. 或重启应用

### 图表不显示？
1. 确认已安装图表依赖：`pip install matplotlib pillow`
2. 检查缓存目录权限
3. 查看日志获取详细错误信息

## 📁 项目结构

```
stock_status_bar/
├── status_bar_app.py              # 应用入口
├── configure.py                   # 配置入口
├── config.json                   # 配置文件
├── cache/                        # 缓存目录
│   ├── charts/                   # 趋势图表缓存
│   └── stock_cache.pkl          # 股票数据缓存
├── tools/                        # 配置工具
│   ├── quick_config.py          # 快捷配置
│   ├── config_gui.py            # 图形配置
│   └── config.py                # 配置查看
├── data_providers/              # 数据提供者
│   ├── stock_provider.py        # 股票数据
│   ├── chart_generator.py       # 图表生成
│   └── ...
├── ui/                          # 用户界面
│   └── status_bar_ui.py         # 状态栏UI
└── utils/                       # 工具类
    ├── icon_manager.py          # 图标管理
    └── thread_manager.py        # 线程管理
```

## 🏗️ 技术架构

### 核心组件
- **应用入口** - 应用主程序
- **控制器** - 业务逻辑控制
- **配置管理** - 配置文件管理，支持热重载
- **数据提供者** - 多种数据获取方式
- **图表生成器** - 高质量趋势图表
- **用户界面** - 状态栏界面管理

### 设计模式
- **工厂模式** - 数据提供者创建
- **观察者模式** - 配置变更通知
- **单例模式** - 线程管理器
- **策略模式** - 不同数据源处理

## 📄 许可证

MIT License

---

💡 **快速上手**：运行 `python3 configure.py` 开始配置你的股票监控！

