# 安装指南

## Windows 系统安装步骤

### 1. 安装 Python

下载并安装 Python 3.10 或 3.11：
- 官网：https://www.python.org/downloads/windows/
- **重要**：安装时勾选 "Add Python to PATH"

验证安装：
```cmd
python --version
```

### 2. 安装虚拟声卡

#### 方案 A：VB-Audio Virtual Cable（推荐）

1. 下载：https://vb-audio.com/Cable/
2. 解压后右键 `VBCABLE_Setup_x64.exe` → "以管理员身份运行"
3. 安装完成后**重启电脑**

#### 方案 B：Voicemeeter

1. 下载：https://vb-audio.com/Voicemeeter/
2. 安装并重启

### 3. 配置音频路由

#### 设置游戏音频输出

1. 右键任务栏音量图标 → "声音设置"
2. 找到游戏进程的音频输出设置
3. 将输出设备改为 **CABLE Input (VB-Audio Virtual Cable)**

#### 设置监听（可选）

如果你想同时听到游戏声音：

1. 右键任务栏音量图标 → "声音" → "录制"
2. 找到 "CABLE Output" → 右键 → "属性"
3. "侦听" 选项卡 → 勾选 "侦听此设备"
4. 选择你的耳机/音箱作为播放设备

### 4. 安装 CUDA（GPU 加速，可选）

如果你有 NVIDIA 显卡：

1. 检查显卡驱动：
   ```cmd
   nvidia-smi
   ```

2. 下载 CUDA Toolkit 11.8：
   - https://developer.nvidia.com/cuda-11-8-0-download-archive
   - 选择 Windows → x86_64 → 版本 → exe(local)

3. 安装（默认选项即可）

### 5. 安装 Python 依赖

打开命令提示符（CMD）或 PowerShell：

```cmd
# 进入项目目录
cd path\to\win_asr_loc

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

**注意**：如果没有 NVIDIA 显卡，安装 CPU 版本的 PyTorch：
```cmd
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 6. 下载翻译模型

```cmd
python scripts/download_models.py
```

这会下载以下翻译包：
- 英语 → 中文
- 俄语 → 英语
- 日语 → 英语
- 韩语 → 英语
- 法语 → 英语
- 德语 → 英语
- 西班牙语 → 英语

**注意**：Whisper 模型会在首次运行时自动下载（约 1.5GB）

### 7. 配置设置

编辑 `config/settings.yaml`：

```yaml
# 音频设备名称（根据你的系统调整）
audio:
  device_name: "CABLE Output"  # 虚拟声卡输出

# Whisper 模型大小
whisper:
  model_size: "medium"  # tiny/base/small/medium/large
  device: "cuda"        # cuda（GPU）或 cpu

# 翻译模式
translation:
  mode: "hybrid"  # local（本地）/ online（在线）/ hybrid（混合）

  # 在线翻译 API（可选）
  online:
    provider: "google"  # google / deepl
    api_key: ""         # DeepL 需要填写 API Key
```

### 8. 运行程序

```cmd
python main.py
```

首次运行会下载 Whisper 模型，请耐心等待。

### 9. 测试

1. 启动游戏
2. 确保游戏音频输出到虚拟声卡
3. 在游戏中说话或播放语音
4. 观察屏幕底部是否出现字幕

---

## 常见问题

### Q1: 提示找不到音频设备

**解决方案**：
1. 检查虚拟声卡是否正确安装
2. 运行测试脚本查看可用设备：
   ```cmd
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```
3. 将输出中的设备名称填入 `config/settings.yaml` 的 `device_name`

### Q2: CUDA 不可用

**解决方案**：
1. 检查 CUDA 是否安装：
   ```cmd
   python -c "import torch; print(torch.cuda.is_available())"
   ```
2. 如果返回 `False`，修改配置文件：
   ```yaml
   whisper:
     device: "cpu"
   ```

### Q3: 识别延迟太高

**解决方案**：
1. 降低模型大小：`model_size: "small"`
2. 减小 beam_size：`beam_size: 1`
3. 启用 GPU 加速

### Q4: 翻译质量差

**解决方案**：
1. 切换到在线翻译：
   ```yaml
   translation:
     mode: "online"
   ```
2. 更新游戏黑话词典：`translation/slang_dict.json`

### Q5: 字幕不显示

**解决方案**：
1. 检查游戏是否全屏（建议使用无边框窗口模式）
2. 调整字幕位置：
   ```yaml
   overlay:
     position: "top"  # 改为顶部
     offset_y: 50
   ```

### Q6: 程序崩溃

**解决方案**：
1. 查看日志文件：`logs/app.log`
2. 检查是否缺少依赖
3. 尝试重新安装依赖：
   ```cmd
   pip install -r requirements.txt --force-reinstall
   ```

---

## 性能优化建议

### 低配置电脑（无独显）

```yaml
whisper:
  model_size: "small"
  device: "cpu"
  compute_type: "int8"
  beam_size: 1

translation:
  mode: "local"  # 避免网络延迟
```

### 高配置电脑（有独显）

```yaml
whisper:
  model_size: "medium"
  device: "cuda"
  compute_type: "float16"
  beam_size: 5

translation:
  mode: "online"  # 更好的翻译质量
  online:
    provider: "deepl"
    api_key: "your-api-key"
```

---

## 卸载

1. 删除项目文件夹
2. 卸载虚拟声卡（控制面板 → 程序和功能）
3. 删除虚拟环境（如果创建了）

---

## 技术支持

遇到问题请查看：
1. 日志文件：`logs/app.log`
2. 项目文档：`README.md`
3. 配置说明：`config/settings.yaml`
