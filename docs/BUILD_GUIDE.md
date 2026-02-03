# 构建指南

## GitHub Actions 自动构建

本项目使用 GitHub Actions 自动构建 Windows 可执行文件。

### 触发构建的方式

#### 1. 创建 Tag（推荐）

```bash
# 创建新版本 tag
git tag -a v1.0.x -m "Release v1.0.x - 描述"

# 推送 tag 触发构建
git push origin v1.0.x
```

构建完成后会自动创建 GitHub Release。

#### 2. 手动触发

1. 访问 GitHub 仓库的 Actions 页面
2. 选择 "Build Windows Executable" workflow
3. 点击 "Run workflow" 按钮
4. 选择分支并运行

手动触发的构建会生成 artifact，但不会创建 Release。

### 构建流程说明

#### 步骤概览

```
1. 检出代码
2. 设置 Python 3.10 环境
3. 安装系统依赖（FFmpeg）
4. 安装 Python 依赖
   - PyTorch (CPU 版本)
   - faster-whisper
   - PyQt5
   - 其他依赖
5. 验证安装
6. 运行 build.py 打包
7. 创建 release 目录结构
8. 生成启动脚本
9. 压缩为 zip 文件
10. 上传 artifact
11. 创建 GitHub Release（仅 tag 触发）
```

#### 构建产物结构

```
游戏翻译助手_v1.0.x.zip
├── 启动翻译助手.bat          # 启动脚本（双击运行）
├── 启动翻译助手/              # 可执行文件目录
│   ├── 启动翻译助手.exe
│   └── [依赖文件...]
├── config/                   # 配置文件
│   └── settings.yaml
├── translation/              # 翻译资源
│   └── slang_dict.json
├── models/                   # 模型目录（空）
├── logs/                     # 日志目录（空）
└── README.md                 # 说明文档
```

### 构建时间

- 完整构建：约 15-20 分钟
- 主要耗时：
  - 安装依赖：8-10 分钟
  - PyInstaller 打包：5-8 分钟
  - 压缩上传：2-3 分钟

### 构建配置

#### PyInstaller 参数

```python
# build.py 中的关键配置
args = [
    '--onedir',              # 目录模式（更稳定）
    '--windowed',            # 无控制台窗口
    '--noupx',               # 不使用 UPX 压缩
    '--add-data=config;config',
    '--add-data=translation/slang_dict.json;translation',
    # ... 隐藏导入
]
```

#### 依赖版本

- Python: 3.10
- PyTorch: CPU 版本（从官方源安装）
- PyQt5: 最新稳定版
- faster-whisper: 最新版

### 错误处理

#### 常见问题

**1. 构建超时**
```yaml
timeout-minutes: 60  # 可在 workflow 中调整
```

**2. 依赖安装失败**
- 检查 pip 源是否可访问
- 查看具体的错误日志
- 可能需要调整依赖版本

**3. 文件复制失败**
- 检查文件路径是否正确
- 确认文件是否存在
- 查看 xcopy 错误码

**4. 压缩失败**
- 检查 release 目录内容
- 确认文件权限
- 查看 PowerShell 错误信息

#### 调试方法

1. **查看构建日志**
   - 访问 Actions 页面
   - 点击失败的 workflow run
   - 展开失败的步骤查看详细日志

2. **验证步骤**
   - "List build output" 显示 dist 目录内容
   - "Verify release contents" 显示 release 目录结构
   - "List release files" 显示生成的 zip 文件

3. **下载 artifact**
   - 即使构建失败，也可能生成部分 artifact
   - 可以下载检查具体问题

### 本地构建

如果需要在本地构建（不推荐，建议使用 GitHub Actions）：

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 2. 运行构建脚本
python build.py

# 3. 检查输出
dir dist\启动翻译助手
```

**注意**：本地构建需要 Windows 环境。

### 优化建议

#### 减少构建时间

1. **使用缓存**
   ```yaml
   - uses: actions/setup-python@v5
     with:
       cache: 'pip'  # 已启用
   ```

2. **并行安装**
   - 当前已优化依赖安装顺序
   - PyTorch 单独安装（最耗时）

3. **减小体积**
   - 排除不需要的模块（已配置）
   - 使用 CPU 版本 PyTorch

#### 提高稳定性

1. **固定依赖版本**
   - 考虑使用 requirements.txt 锁定版本
   - 避免依赖更新导致的构建失败

2. **增加重试机制**
   ```yaml
   - uses: nick-invision/retry@v2
     with:
       timeout_minutes: 10
       max_attempts: 3
   ```

3. **分阶段构建**
   - 可以考虑将依赖安装和打包分离
   - 使用 Docker 镜像预装依赖

### Release 管理

#### 版本号规范

遵循语义化版本：`vMAJOR.MINOR.PATCH`

- MAJOR: 重大更新，不兼容的 API 变更
- MINOR: 新功能，向后兼容
- PATCH: Bug 修复，向后兼容

示例：
```bash
v1.0.0  # 首次发布
v1.0.1  # Bug 修复
v1.1.0  # 新功能
v2.0.0  # 重大更新
```

#### Release 内容

自动生成的 Release 包含：
- 📦 下载说明
- ✨ 功能特性
- 📋 系统要求
- 🔗 自动生成的更新日志

### 安全注意事项

1. **GITHUB_TOKEN**
   - 自动提供，无需手动配置
   - 仅用于创建 Release

2. **依赖安全**
   - 定期更新依赖版本
   - 使用 `pip audit` 检查漏洞

3. **代码签名**
   - 当前未配置代码签名
   - 用户可能看到 Windows SmartScreen 警告
   - 未来可考虑添加代码签名证书

### 监控和维护

#### 定期检查

- [ ] 每月检查依赖更新
- [ ] 测试新版本 Python 兼容性
- [ ] 验证构建流程正常
- [ ] 检查 GitHub Actions 配额使用情况

#### 性能指标

- 构建成功率：目标 > 95%
- 平均构建时间：< 20 分钟
- 产物大小：< 500 MB

---

## 相关文档

- [CHANGELOG.md](../CHANGELOG.md) - 版本更新日志
- [README.md](../README.md) - 项目说明
- [build.py](../build.py) - 构建脚本
