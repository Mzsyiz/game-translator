# Mac 上打包 Windows 程序指南

## ⚠️ 重要说明

**PyInstaller 打包必须在目标操作系统上进行！**

- 在 Mac 上打包 → 只能生成 Mac 应用
- 在 Windows 上打包 → 才能生成 Windows exe

因此，您有以下几种选择：

---

## 🎯 推荐方案

### 方案 A：GitHub Actions 自动打包（最简单）⭐⭐⭐⭐⭐

**优点**：
- ✅ 完全自动化
- ✅ 无需本地 Windows 环境
- ✅ 免费使用
- ✅ 可重复构建

**步骤**：

1. **初始化 Git 仓库**（如果还没有）
   ```bash
   cd /Users/mzsyiz/project/test/win_asr_loc
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **创建 GitHub 仓库**
   - 访问 https://github.com/new
   - 创建新仓库（例如：game-translator）
   - 不要初始化 README

3. **推送代码到 GitHub**
   ```bash
   git remote add origin https://github.com/你的用户名/game-translator.git
   git branch -M main
   git push -u origin main
   ```

4. **触发自动构建**

   **方式 1：创建 Tag**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

   **方式 2：手动触发**
   - 访问 GitHub 仓库页面
   - 点击 "Actions" 标签
   - 选择 "Build Windows Executable"
   - 点击 "Run workflow"

5. **下载构建结果**
   - 等待构建完成（约 10-15 分钟）
   - 在 Actions 页面下载 "游戏翻译助手" artifact
   - 解压得到 `游戏翻译助手_v1.0.0.zip`

---

### 方案 B：使用虚拟机打包 ⭐⭐⭐⭐

**优点**：
- ✅ 完全控制构建环境
- ✅ 可以本地测试

**缺点**：
- ❌ 需要 Windows 许可证
- ❌ 占用磁盘空间

**步骤**：

1. **安装虚拟机软件**

   **Parallels Desktop**（推荐）：
   ```bash
   # 下载：https://www.parallels.com/
   # 免费试用 14 天
   ```

   **VMware Fusion**：
   ```bash
   # 下载：https://www.vmware.com/products/fusion.html
   # 个人使用免费
   ```

2. **创建 Windows 虚拟机**
   - 安装 Windows 10 或 11
   - 分配至少 8GB 内存
   - 分配至少 50GB 磁盘

3. **在虚拟机中打包**
   ```cmd
   # 1. 将项目文件复制到虚拟机
   # 2. 安装 Python 3.10+
   # 3. 打开 PowerShell 或 CMD

   cd win_asr_loc
   pip install -r requirements.txt
   pip install pyinstaller
   python build.py
   python create_release.py
   ```

4. **复制打包结果**
   - 打包完成后，在 `release/` 目录找到 zip 文件
   - 复制回 Mac

---

### 方案 C：使用云服务器打包 ⭐⭐⭐

**优点**：
- ✅ 按需使用
- ✅ 成本低

**步骤**：

1. **租用 Windows 云服务器**
   - AWS EC2（Windows Server）
   - Azure Virtual Machines
   - 阿里云 ECS（Windows）
   - 腾讯云 CVM（Windows）

2. **远程连接**
   ```bash
   # Mac 上使用 Microsoft Remote Desktop
   # 下载：https://apps.apple.com/app/microsoft-remote-desktop/id1295203466
   ```

3. **上传项目文件**
   ```bash
   # 使用 scp 或 SFTP
   scp -r win_asr_loc user@server:/path/
   ```

4. **在服务器上打包**
   ```cmd
   cd win_asr_loc
   pip install -r requirements.txt
   pip install pyinstaller
   python build.py
   python create_release.py
   ```

5. **下载打包结果**
   ```bash
   scp user@server:/path/win_asr_loc/release/*.zip .
   ```

---

### 方案 D：直接在 Windows 电脑上打包 ⭐⭐⭐⭐⭐

**如果您有 Windows 电脑**：

1. **复制项目文件到 Windows**
   - 使用 U 盘
   - 或通过网络共享
   - 或通过 Git

2. **在 Windows 上打包**
   ```cmd
   cd win_asr_loc
   pip install -r requirements.txt
   pip install pyinstaller
   python build.py
   python create_release.py
   ```

3. **获取打包结果**
   - 在 `release/` 目录找到 zip 文件

---

## 🚀 快速开始（推荐 GitHub Actions）

### 完整命令

```bash
# 1. 进入项目目录
cd /Users/mzsyiz/project/test/win_asr_loc

# 2. 初始化 Git（如果还没有）
git init
git add .
git commit -m "Initial commit: 游戏实时语音翻译工具"

# 3. 创建 GitHub 仓库并推送
# 先在 GitHub 网站上创建仓库，然后：
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main

# 4. 创建 Tag 触发构建
git tag v1.0.0
git push origin v1.0.0

# 5. 等待构建完成（10-15 分钟）
# 访问 https://github.com/你的用户名/仓库名/actions

# 6. 下载构建结果
# 在 Actions 页面下载 artifact
```

---

## 📦 打包结果

打包完成后，您将得到：

```
游戏翻译助手_v1.0.0.zip (约 500MB-1GB)
├── 首次使用必读.txt
├── 首次使用向导.bat
├── 下载虚拟声卡.url
├── 启动翻译助手.exe          # 主程序
├── config/
│   └── settings.yaml
├── translation/
│   └── slang_dict.json
├── docs/
│   ├── README.md
│   ├── QUICKSTART.md
│   └── INSTALL.md
├── models/
└── logs/
```

---

## 🧪 在 Windows 上测试

1. **解压 zip 文件**
   ```
   右键 → 解压到当前文件夹
   ```

2. **阅读说明**
   ```
   双击打开「首次使用必读.txt」
   ```

3. **安装虚拟声卡**
   ```
   双击运行「首次使用向导.bat」
   按照提示完成安装
   重启电脑
   ```

4. **启动程序**
   ```
   双击运行「启动翻译助手.exe」
   ```

5. **测试功能**
   - 检查是否能正常启动
   - 检查音频设备列表
   - 测试音频捕获
   - 测试语音识别
   - 测试翻译功能
   - 测试字幕显示

---

## ❓ 常见问题

### Q: GitHub Actions 构建失败？

A: 检查以下几点：
- requirements.txt 中的依赖是否都能在 Windows 上安装
- build.py 中的路径是否正确
- 是否有足够的构建时间（GitHub Actions 免费版有 6 小时限制）

### Q: 打包后的文件太大？

A: 可以优化：
- 在 build.py 中排除不需要的模块
- 使用更小的 Whisper 模型
- 使用 `--onedir` 模式而不是 `--onefile`

### Q: 打包后运行报错？

A: 常见原因：
- 缺少隐藏导入：在 build.py 中添加 `--hidden-import=模块名`
- 数据文件路径错误：检查 `--add-data` 参数
- 依赖库版本不兼容：固定 requirements.txt 中的版本号

---

## 📚 参考资料

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Parallels Desktop](https://www.parallels.com/)
- [VMware Fusion](https://www.vmware.com/products/fusion.html)

---

## ✅ 推荐流程

**对于您的情况，我推荐：**

1. ✅ **使用 GitHub Actions 自动打包**（最简单）
   - 无需本地 Windows 环境
   - 完全自动化
   - 免费使用

2. ✅ **下载构建结果**
   - 等待 10-15 分钟
   - 下载 zip 文件

3. ✅ **在 Windows 电脑上测试**
   - 解压并运行
   - 测试所有功能

---

**准备好了吗？让我们开始吧！** 🚀
