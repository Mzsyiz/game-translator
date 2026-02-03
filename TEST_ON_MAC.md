# Mac 上测试指南

## 🍎 在 Mac 上可以做什么

虽然这是一个 Windows 专用工具，但在 Mac 上您可以：

### ✅ 可以测试的部分

1. **代码质量检查**
2. **模块导入测试**
3. **配置文件验证**
4. **文档完整性检查**
5. **项目结构验证**

### ❌ 无法测试的部分

1. **虚拟声卡音频捕获**（Windows 专用）
2. **实际的语音识别**（需要音频输入）
3. **字幕窗口显示**（Windows 窗口 API）
4. **完整的端到端流程**

---

## 🚀 快速测试（3 步）

### 步骤 1：运行测试脚本

```bash
cd /Users/mzsyiz/project/test/win_asr_loc
./test_on_mac.sh
```

这将自动检查：
- Python 环境
- 项目文件
- 目录结构
- Python 依赖
- 配置文件
- 模块导入
- 文档完整性

### 步骤 2：查看测试结果

测试脚本会显示：
- ✓ 通过的测试（绿色）
- ✗ 失败的测试（红色）
- ⊘ 跳过的测试（黄色，Windows 专用）

### 步骤 3：修复问题（如果有）

如果有测试失败，按照提示修复问题。

---

## 📦 打包 Windows 程序

### 推荐方案：GitHub Actions 自动打包

**优点**：
- ✅ 无需本地 Windows 环境
- ✅ 完全自动化
- ✅ 免费使用

**步骤**：

```bash
# 1. 运行部署脚本
./deploy_to_github.sh

# 2. 按照提示操作：
#    - 在 GitHub 创建新仓库
#    - 输入仓库 URL
#    - 等待自动推送

# 3. 访问 GitHub Actions 查看构建进度
#    https://github.com/你的用户名/仓库名/actions

# 4. 等待 10-15 分钟

# 5. 下载构建结果
#    在 Actions 页面下载 "游戏翻译助手" artifact
```

---

## 🧪 详细测试步骤

### 1. 检查 Python 环境

```bash
python3 --version
# 应该显示 Python 3.10 或更高版本
```

### 2. 安装依赖（可选）

```bash
pip3 install pyyaml loguru numpy
```

### 3. 测试配置文件

```bash
# 测试 YAML 配置
python3 -c "import yaml; print(yaml.safe_load(open('config/settings.yaml')))"

# 测试 JSON 词典
python3 -c "import json; print(len(json.load(open('translation/slang_dict.json'))), '个词条')"
```

### 4. 测试模块导入

```bash
# 测试 audio 模块
python3 -c "import sys; sys.path.insert(0, '.'); from audio import capture, vad, processor; print('✓ audio 模块正常')"

# 测试 asr 模块
python3 -c "import sys; sys.path.insert(0, '.'); from asr import whisper_engine; print('✓ asr 模块正常')"

# 测试 translation 模块
python3 -c "import sys; sys.path.insert(0, '.'); from translation import translator_manager; print('✓ translation 模块正常')"

# 测试 overlay 模块
python3 -c "import sys; sys.path.insert(0, '.'); from overlay import subtitle_window; print('✓ overlay 模块正常')"
```

### 5. 检查文件完整性

```bash
# 检查所有 Python 文件
find . -name "*.py" -not -path "./venv/*" | wc -l

# 检查所有文档
ls -lh *.md

# 检查配置文件
ls -lh config/*.yaml translation/*.json
```

---

## 📊 测试清单

### 代码质量
- [ ] Python 版本 >= 3.10
- [ ] 所有 Python 文件无语法错误
- [ ] 配置文件格式正确
- [ ] 词典文件格式正确

### 项目结构
- [ ] 主程序文件存在 (main.py)
- [ ] 所有模块目录存在 (audio/, asr/, translation/, overlay/)
- [ ] 配置目录存在 (config/)
- [ ] 脚本目录存在 (scripts/)

### 模块导入
- [ ] audio 模块可以导入
- [ ] asr 模块可以导入
- [ ] translation 模块可以导入
- [ ] overlay 模块可以导入

### 文档完整性
- [ ] README.md 存在
- [ ] INSTALL.md 存在
- [ ] QUICKSTART.md 存在
- [ ] 其他文档存在

---

## 🎯 下一步

### 在 Mac 上完成测试后：

1. **部署到 GitHub**
   ```bash
   ./deploy_to_github.sh
   ```

2. **等待自动构建**
   - 访问 GitHub Actions 页面
   - 等待 10-15 分钟

3. **下载构建结果**
   - 下载 `游戏翻译助手_v1.0.0.zip`

4. **在 Windows 上测试**
   - 将 zip 文件复制到 Windows 电脑
   - 解压并运行
   - 测试所有功能

---

## ❓ 常见问题

### Q: 测试脚本报错 "command not found"？

A: 确保脚本有执行权限：
```bash
chmod +x test_on_mac.sh
./test_on_mac.sh
```

### Q: 模块导入失败？

A: 安装缺失的依赖：
```bash
pip3 install -r requirements.txt
```

### Q: 如何跳过 Windows 专用测试？

A: 测试脚本会自动跳过 Windows 专用功能，显示为 "⊘ 跳过"

---

## 📚 相关文档

- `MAC_BUILD_GUIDE.md` - Mac 上打包 Windows 程序的完整指南
- `BUILD_GUIDE.md` - 打包和发布指南
- `OPTIMIZATION_GUIDE.md` - 用户体验优化指南

---

**准备好了吗？运行测试脚本开始吧！** 🚀

```bash
./test_on_mac.sh
```
