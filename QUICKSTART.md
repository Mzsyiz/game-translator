# 快速开始指南

## 🚀 5 分钟快速上手

### 第一步：安装虚拟声卡

1. 下载 VB-Audio Virtual Cable：https://vb-audio.com/Cable/
2. 解压后右键 `VBCABLE_Setup_x64.exe` → "以管理员身份运行"
3. 安装完成后**重启电脑**

### 第二步：配置游戏音频

1. 右键任务栏音量图标 → "声音设置"
2. 找到你的游戏进程
3. 将输出设备改为 **CABLE Input (VB-Audio Virtual Cable)**

### 第三步：安装程序

双击运行 `install.bat`，等待安装完成（首次安装约需 10-15 分钟）

### 第四步：测试音频

运行测试脚本：
```cmd
python test_audio.py
```

如果看到音量条跳动，说明配置成功！

### 第五步：启动程序

双击运行 `run.bat`

---

## ⚙️ 配置调整

编辑 `config/settings.yaml`：

### 如果没有 NVIDIA 显卡

```yaml
whisper:
  device: "cpu"
  model_size: "small"
```

### 如果延迟太高

```yaml
whisper:
  model_size: "small"
  beam_size: 1
```

### 如果翻译质量差

```yaml
translation:
  mode: "online"
  online:
    provider: "google"
```

---

## 🎮 使用技巧

### 1. 游戏设置建议

- **窗口模式**：使用"无边框窗口"而不是全屏
- **音量**：游戏音量调到 50-70%
- **语音**：队友语音清晰度很重要

### 2. 字幕位置调整

如果字幕被遮挡，修改配置：

```yaml
overlay:
  position: "top"    # 改为顶部
  offset_y: 50       # 距离边缘 50 像素
```

### 3. 添加游戏黑话

编辑 `translation/slang_dict.json`：

```json
{
  "rush B": "冲 B 点",
  "eco round": "eco 局",
  "gg": "打得好"
}
```

---

## ❓ 常见问题

### Q: 没有声音/字幕不显示

**检查清单**：
1. ✅ 虚拟声卡已安装并重启
2. ✅ 游戏音频输出到 CABLE Input
3. ✅ 运行 `test_audio.py` 能看到音量条
4. ✅ 游戏使用无边框窗口模式

### Q: 延迟太高（超过 2 秒）

**解决方案**：
1. 降低模型大小：`model_size: "small"`
2. 减小 beam_size：`beam_size: 1`
3. 启用 GPU：`device: "cuda"`（需要 NVIDIA 显卡）

### Q: 识别不准确

**解决方案**：
1. 提高模型大小：`model_size: "medium"`
2. 确保游戏音量适中（50-70%）
3. 减少背景噪音

### Q: 程序崩溃

**解决方案**：
1. 查看日志：`logs/app.log`
2. 重新安装依赖：
   ```cmd
   pip install -r requirements.txt --force-reinstall
   ```

---

## 📊 性能参考

| 配置 | 模型 | 延迟 | 准确度 |
|------|------|------|--------|
| 无独显 | small + CPU | 2-3s | 中 |
| GTX 1660 | medium + GPU | 0.8-1.2s | 高 |
| RTX 3060 | medium + GPU | 0.6-0.9s | 高 |
| RTX 4070 | large + GPU | 0.8-1.0s | 很高 |

---

## 🎯 推荐配置

### 最佳平衡（推荐）

```yaml
whisper:
  model_size: "medium"
  device: "cuda"
  beam_size: 5

translation:
  mode: "hybrid"
```

### 最低延迟

```yaml
whisper:
  model_size: "small"
  device: "cuda"
  beam_size: 1

translation:
  mode: "local"
```

### 最高质量

```yaml
whisper:
  model_size: "medium"
  device: "cuda"
  beam_size: 5

translation:
  mode: "online"
  online:
    provider: "deepl"
```

---

## 🔧 高级功能

### 自定义快捷键（TODO）

目前快捷键硬编码，未来版本将支持自定义。

### 多显示器支持

字幕会显示在主显示器上，如果需要调整：

```yaml
overlay:
  offset_x: 1920  # 移动到第二个显示器
```

### 录制功能（TODO）

未来版本将支持保存识别和翻译记录。

---

## 📝 反馈与支持

遇到问题请提供：
1. 日志文件：`logs/app.log`
2. 配置文件：`config/settings.yaml`
3. 系统信息：Windows 版本、显卡型号
4. 问题描述：具体现象、复现步骤

---

**祝你游戏愉快！🎮**
