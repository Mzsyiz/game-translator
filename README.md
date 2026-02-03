# 游戏实时语音翻译工具

## 项目简介

Windows 平台游戏语音实时翻译字幕工具，通过虚拟声卡捕获游戏语音，使用 Whisper 进行多语言识别，支持本地和在线翻译，以透明字幕形式显示。

**核心特性**：
- ✅ 系统级音频捕获（安全，不接触游戏进程）
- ✅ 多语言自动识别（Whisper）
- ✅ 双翻译引擎（本地 Argos + 在线 DeepL/Google）
- ✅ 透明字幕 Overlay（置顶、鼠标穿透）
- ✅ 低延迟优化（目标 0.6-1.2s）

## 系统要求

### 硬件
- Windows 10/11
- CPU: Intel i5 / AMD Ryzen 5 及以上
- 内存: 16GB 推荐
- 显卡: NVIDIA GTX 1660+ (支持 CUDA)

### 软件依赖
- Python 3.10+
- CUDA Toolkit 11.8+ (GPU 加速)
- VB-Audio Virtual Cable (虚拟声卡)

## 快速开始

### 1. 安装虚拟声卡
下载并安装 [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)

### 2. 配置音频路由
```
游戏音频输出 → CABLE Input (VB-Audio Virtual Cable)
监听设备 → CABLE Output
```

### 3. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 4. 下载翻译模型（本地翻译）
```bash
python scripts/download_models.py
```

### 5. 配置设置
编辑 `config/settings.yaml`：
```yaml
translation:
  mode: "local"  # local / online / hybrid
  online_api: "deepl"  # deepl / google
  api_key: "your-api-key-here"
```

### 6. 运行
```bash
python main.py
```

## 项目结构

```
win_asr_loc/
├─ audio/                   # 音频处理模块
│  ├─ capture.py           # 虚拟声卡音频捕获
│  ├─ vad.py               # 语音活动检测
│  └─ processor.py         # 音频预处理
│
├─ asr/                     # 语音识别模块
│  └─ whisper_engine.py    # Whisper 引擎封装
│
├─ translation/             # 翻译模块
│  ├─ local_translator.py  # 本地翻译 (Argos)
│  ├─ online_translator.py # 在线翻译 (DeepL/Google)
│  ├─ translator_manager.py # 翻译管理器
│  └─ slang_dict.json      # 游戏黑话词典
│
├─ overlay/                 # 字幕显示模块
│  ├─ subtitle_window.py   # 透明字幕窗口
│  └─ styles.py            # 字幕样式配置
│
├─ config/                  # 配置文件
│  └─ settings.yaml        # 主配置文件
│
├─ scripts/                 # 工具脚本
│  └─ download_models.py   # 模型下载脚本
│
├─ main.py                  # 程序入口
├─ requirements.txt         # Python 依赖
└─ README.md               # 项目文档
```

## 使用说明

### 翻译模式切换

**本地翻译（离线）**：
- 优点：完全离线，无 API 费用
- 缺点：翻译质量略低于在线服务
- 适用：隐私敏感、网络不稳定场景

**在线翻译**：
- 优点：翻译质量高，支持更多语言
- 缺点：需要网络，可能有 API 费用
- 适用：追求翻译质量场景

**混合模式**：
- 本地翻译失败时自动切换在线翻译

### 快捷键

- `Ctrl + Shift + S`: 开始/停止捕获
- `Ctrl + Shift + H`: 隐藏/显示字幕
- `Ctrl + Shift + Q`: 退出程序

### 游戏黑话词典

编辑 `translation/slang_dict.json` 添加游戏术语：
```json
{
  "rat": "蹲逼",
  "push": "冲",
  "camp": "卡点",
  "one tap": "秒头",
  "behind": "后面",
  "grenade": "雷"
}
```

## 性能优化

### 延迟优化
- 使用 `medium` 模型（平衡速度和准确度）
- 启用 VAD（语音活动检测）
- 音频切片 200-500ms
- beam_size ≤ 5

### GPU 加速
确保安装了 CUDA Toolkit 并正确配置：
```bash
# 检查 CUDA 是否可用
python -c "import torch; print(torch.cuda.is_available())"
```

## 故障排除

### 无法捕获音频
1. 检查虚拟声卡是否正确安装
2. 确认游戏音频输出到 CABLE Input
3. 检查 Windows 音频设备设置

### 识别延迟过高
1. 降低 Whisper 模型大小（使用 small）
2. 启用 GPU 加速
3. 调整音频切片大小

### 翻译质量差
1. 切换到在线翻译模式
2. 更新游戏黑话词典
3. 检查源语言识别是否正确

## 安全说明

本工具采用系统级音频捕获，**不接触游戏进程**：
- ✅ 不注入 DLL
- ✅ 不 Hook 游戏函数
- ✅ 不读取游戏内存
- ✅ 不修改游戏文件

**原理等同于 OBS 录音或 Discord 语音监听，无封号风险。**

## 开发路线

- [x] Phase 1: 核心功能实现
- [x] Phase 2: 双翻译引擎支持
- [ ] Phase 3: 性能优化
- [ ] Phase 4: UI 美化
- [ ] Phase 5: 打包发布

## 许可证

MIT License - 仅供个人学习使用

## 免责声明

本工具仅用于辅助理解游戏语音交流，不提供任何游戏优势。使用者需自行承担使用风险。
