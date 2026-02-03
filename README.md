# 🎮 游戏实时语音翻译助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

> 🚀 实时捕获游戏语音，AI 识别并翻译，透明字幕显示 - 让语言不再是游戏障碍

## ✨ 核心特性

- 🎯 **系统级音频捕获** - 安全无侵入，不接触游戏进程
- 🌍 **多语言自动识别** - 基于 OpenAI Whisper，支持 99+ 语言
- 🔄 **双翻译引擎** - 本地离线翻译 + 在线高质量翻译
- 💬 **透明字幕显示** - 置顶窗口，鼠标穿透，不影响游戏操作
- ⚡ **低延迟优化** - 端到端延迟 0.6-1.2 秒
- 🎮 **游戏术语优化** - 内置黑话词典，准确翻译游戏用语

## 📋 系统要求

### 最低配置
- **操作系统**: Windows 10/11 (64-bit)
- **处理器**: Intel i5 / AMD Ryzen 5
- **内存**: 8GB RAM
- **存储**: 5GB 可用空间

### 推荐配置
- **处理器**: Intel i7 / AMD Ryzen 7
- **内存**: 16GB RAM
- **显卡**: NVIDIA GTX 1660+ (支持 CUDA 加速)

### 必需软件
- [Python 3.10+](https://www.python.org/downloads/)
- [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) (虚拟声卡)
- [CUDA Toolkit 11.8+](https://developer.nvidia.com/cuda-downloads) (可选，GPU 加速)

## 🚀 快速开始

### 方法一：使用预编译版本（推荐）

1. **下载发布包**
   ```
   前往 Releases 页面下载最新版本
   解压到任意目录
   ```

2. **安装虚拟声卡**
   ```
   双击运行「首次使用向导.bat」
   按照提示完成虚拟声卡安装
   重启电脑
   ```

3. **配置游戏音频**
   ```
   右键任务栏音量图标 → 打开声音设置
   找到游戏进程 → 输出设备改为「CABLE Input」
   ```

4. **启动程序**
   ```
   双击「启动翻译助手.exe」
   开始游戏，享受实时翻译！
   ```

### 方法二：从源码运行

1. **克隆仓库**
   ```bash
   git clone https://github.com/Mzsyiz/game-translator.git
   cd game-translator
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **下载翻译模型**（本地翻译模式需要）
   ```bash
   python scripts/download_models.py
   ```

4. **配置设置**

   编辑 `config/settings.yaml`：
   ```yaml
   # 音频捕获设置
   audio:
     device_name: "CABLE Output"
     sample_rate: 16000
     chunk_duration: 0.3

   # Whisper 识别设置
   whisper:
     model_size: "medium"  # tiny/small/medium/large
     device: "cuda"        # cuda/cpu
     language: "auto"      # auto 或指定语言代码

   # 翻译设置
   translation:
     mode: "local"         # local/online/hybrid
     target_language: "zh"

     # 在线翻译 API（可选）
     online_api: "deepl"   # deepl/google
     api_key: ""           # 填入你的 API Key

   # 字幕显示设置
   overlay:
     position: "bottom"    # top/bottom/custom
     font_size: 32
     opacity: 0.9
   ```

5. **运行程序**
   ```bash
   python main.py
   ```

## 📖 使用指南

### 翻译模式选择

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **本地翻译** | 完全离线，无费用 | 质量略低 | 隐私敏感、网络不稳定 |
| **在线翻译** | 质量高，支持更多语言 | 需要网络和 API Key | 追求翻译质量 |
| **混合模式** | 兼顾速度和质量 | 需配置在线 API | 日常使用推荐 |

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + Shift + S` | 开始/停止捕获 |
| `Ctrl + Shift + H` | 隐藏/显示字幕 |
| `Ctrl + Shift + Q` | 退出程序 |

### 游戏术语词典

编辑 `translation/slang_dict.json` 添加游戏专用术语：

```json
{
  "rat": "蹲逼",
  "push": "冲",
  "camp": "卡点",
  "one tap": "秒头",
  "behind": "后面",
  "nade": "雷",
  "rotate": "转点",
  "eco": "存钱局"
}
```

## ⚙️ 性能优化

### 降低延迟

1. **使用更小的 Whisper 模型**
   ```yaml
   whisper:
     model_size: "small"  # medium → small
     beam_size: 1         # 降低 beam size
   ```

2. **启用 GPU 加速**
   ```yaml
   whisper:
     device: "cuda"
   ```

   验证 CUDA 是否可用：
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **调整音频切片**
   ```yaml
   audio:
     chunk_duration: 0.2  # 减小切片时长
   ```

### 提高准确度

1. **使用更大的模型**
   ```yaml
   whisper:
     model_size: "large"
     beam_size: 5
   ```

2. **指定源语言**
   ```yaml
   whisper:
     language: "en"  # 不使用 auto
   ```

3. **切换在线翻译**
   ```yaml
   translation:
     mode: "online"
     online_api: "deepl"
   ```

## 🛠️ 故障排除

### ❌ 无法捕获音频

**症状**: 程序运行但没有识别到语音

**解决方案**:
1. 检查虚拟声卡是否安装：
   ```
   控制面板 → 声音 → 录制 → 查看是否有 "CABLE Output"
   ```

2. 确认游戏音频路由：
   ```
   设置 → 系统 → 声音 → 应用音量和设备首选项
   找到游戏 → 输出改为 "CABLE Input"
   ```

3. 测试音频捕获：
   ```bash
   python test_audio.py
   ```

### ⏱️ 延迟过高

**症状**: 字幕显示延迟超过 2 秒

**解决方案**:
1. 降低模型大小：`medium` → `small`
2. 启用 GPU 加速（需要 NVIDIA 显卡）
3. 减小音频切片时长：`0.3` → `0.2`
4. 关闭其他占用 GPU 的程序

### 🔤 翻译质量差

**症状**: 翻译不准确或出现乱码

**解决方案**:
1. 切换到在线翻译模式
2. 更新游戏术语词典
3. 指定源语言（不使用 auto）
4. 检查游戏音量（不要太小或太大）

### 💥 程序崩溃

**症状**: 程序启动后立即退出

**解决方案**:
1. 查看日志文件：`logs/app.log`
2. 确认虚拟声卡已安装并重启电脑
3. 检查 Python 版本：`python --version` (需要 3.10+)
4. 重新安装依赖：`pip install -r requirements.txt --force-reinstall`

## 🔒 安全说明

本工具采用**系统级音频捕获**，完全不接触游戏进程：

✅ **不注入游戏进程** - 不使用 DLL 注入
✅ **不修改游戏文件** - 不改动任何游戏数据
✅ **不读取游戏内存** - 不访问游戏内存空间
✅ **不 Hook 游戏函数** - 不拦截游戏 API 调用

**工作原理**: 等同于 OBS 录音或 Discord 语音监听，通过虚拟声卡捕获系统音频流。

**结论**: 无封号风险，可以放心使用。

## 📁 项目结构

```
game-translator/
├── audio/                    # 音频处理模块
│   ├── capture.py           # 虚拟声卡音频捕获
│   ├── vad.py               # 语音活动检测 (VAD)
│   └── processor.py         # 音频预处理
│
├── asr/                      # 语音识别模块
│   └── whisper_engine.py    # Whisper 引擎封装
│
├── translation/              # 翻译模块
│   ├── local_translator.py  # 本地翻译 (Argos Translate)
│   ├── online_translator.py # 在线翻译 (DeepL/Google)
│   ├── translator_manager.py# 翻译管理器
│   └── slang_dict.json      # 游戏术语词典
│
├── overlay/                  # 字幕显示模块
│   └── subtitle_window.py   # 透明字幕窗口
│
├── config/                   # 配置文件
│   └── settings.yaml        # 主配置文件
│
├── scripts/                  # 工具脚本
│   └── download_models.py   # 模型下载脚本
│
├── .github/workflows/        # GitHub Actions
│   └── build.yml            # 自动构建配置
│
├── main.py                   # 程序入口
├── build.py                  # 打包脚本
├── test_audio.py            # 音频测试工具
├── setup_wizard.py          # 安装向导
├── requirements.txt         # Python 依赖
└── README.md                # 项目文档
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 添加必要的注释和文档字符串
- 提交前运行测试：`pytest tests/`

## 📝 更新日志

### v1.0.1 (2026-02-03)
- ✨ 添加 GitHub Actions 自动构建
- 🐛 修复 Windows 打包问题
- 📝 更新文档和使用指南

### v1.0.0 (2026-02-01)
- 🎉 首次发布
- ✅ 实现核心功能：音频捕获、语音识别、翻译、字幕显示
- ✅ 支持本地和在线双翻译引擎
- ✅ 游戏术语词典支持

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

**仅供个人学习和研究使用，请勿用于商业用途。**

## ⚠️ 免责声明

- 本工具仅用于辅助理解游戏语音交流，不提供任何游戏优势
- 使用者需自行承担使用风险
- 开发者不对因使用本工具导致的任何问题负责
- 请遵守游戏服务条款和当地法律法规

## 💬 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/Mzsyiz/game-translator/issues)
- **功能建议**: [GitHub Discussions](https://github.com/Mzsyiz/game-translator/discussions)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by [Mzsyiz](https://github.com/Mzsyiz)

</div>
