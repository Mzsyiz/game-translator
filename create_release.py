#!/usr/bin/env python3
"""
创建发布包
将打包好的程序和相关文件整理成发布包
"""
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_release():
    """创建发布包"""

    print("=" * 60)
    print("  游戏翻译助手 - 创建发布包")
    print("=" * 60)
    print()

    # 检查主程序是否存在（支持两种打包模式）
    exe_path_onefile = Path("dist/启动翻译助手.exe")
    exe_path_onedir = Path("dist/启动翻译助手/启动翻译助手.exe")
    dist_dir = Path("dist/启动翻译助手")

    if exe_path_onefile.exists():
        # 单文件模式
        exe_path = exe_path_onefile
        is_onedir = False
        print("检测到单文件打包模式")
    elif exe_path_onedir.exists():
        # 目录模式
        exe_path = exe_path_onedir
        is_onedir = True
        print("检测到目录打包模式")
    else:
        print("❌ 未找到主程序")
        print("\n请先运行: python build.py")
        print(f"\n查找路径：")
        print(f"  - {exe_path_onefile}")
        print(f"  - {exe_path_onedir}")
        return

    # 版本号
    version = "v1.0.0"
    release_name = f"游戏翻译助手_{version}"
    release_dir = Path("release") / release_name

    print(f"[1/5] 创建目录结构...")

    # 清理旧的发布包
    if release_dir.exists():
        shutil.rmtree(release_dir)

    # 创建目录
    release_dir.mkdir(parents=True, exist_ok=True)
    (release_dir / "drivers").mkdir(exist_ok=True)
    (release_dir / "docs").mkdir(exist_ok=True)
    (release_dir / "models").mkdir(exist_ok=True)
    (release_dir / "logs").mkdir(exist_ok=True)

    print("  ✓ 目录创建完成")

    print("\n[2/5] 复制主程序...")

    # 复制主程序
    if is_onedir:
        # 目录模式：复制整个目录
        shutil.copytree(dist_dir, release_dir / "app")
        # 创建启动脚本
        create_launcher_bat(release_dir)
        print("  ✓ app/ (包含所有依赖)")
        print("  ✓ 启动翻译助手.bat (启动脚本)")
    else:
        # 单文件模式：直接复制 exe
        shutil.copy(exe_path, release_dir / "启动翻译助手.exe")
        print("  ✓ 启动翻译助手.exe")

    print("\n[3/5] 复制配置文件...")

    # 复制配置
    shutil.copytree("config", release_dir / "config")
    print("  ✓ config/")

    # 复制黑话词典
    (release_dir / "translation").mkdir(exist_ok=True)
    shutil.copy("translation/slang_dict.json", release_dir / "translation/")
    print("  ✓ translation/slang_dict.json")

    print("\n[4/5] 创建文档和脚本...")

    # 创建首次使用必读
    create_readme(release_dir)
    print("  ✓ 首次使用必读.txt")

    # 创建首次使用向导
    create_setup_wizard_bat(release_dir)
    print("  ✓ 首次使用向导.bat")

    # 创建虚拟声卡下载链接
    create_driver_link(release_dir)
    print("  ✓ 下载虚拟声卡.url")

    # 复制文档
    for doc in ["README.md", "QUICKSTART.md", "INSTALL.md"]:
        if Path(doc).exists():
            shutil.copy(doc, release_dir / "docs" / doc)
            print(f"  ✓ docs/{doc}")

    # 创建 .gitkeep
    (release_dir / "models" / ".gitkeep").touch()
    (release_dir / "logs" / ".gitkeep").touch()

    print("\n[5/5] 打包成 ZIP...")

    # 打包成 zip
    zip_path = Path("release") / f"{release_name}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in release_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(release_dir.parent)
                zipf.write(file, arcname)

    print(f"  ✓ {zip_path.name}")

    # 统计信息
    print("\n" + "=" * 60)
    print("  发布包创建完成！")
    print("=" * 60)
    print(f"\n📦 发布包位置: {zip_path}")
    print(f"📊 文件大小: {get_file_size(zip_path)}")
    print(f"📁 解压后目录: {release_dir}")
    print()
    print("下一步：")
    print("1. 测试发布包")
    print("2. 上传到 GitHub Releases")
    print("3. 分享给用户")
    print()


def create_readme(release_dir):
    """创建首次使用必读"""
    content = """═══════════════════════════════════════════════════════════
          游戏翻译助手 v1.0 - 3 步快速开始
═══════════════════════════════════════════════════════════

第 1 步：安装虚拟声卡（仅首次需要）
  → 双击运行「首次使用向导.bat」
  → 或手动下载：双击「下载虚拟声卡.url」
  → 按照提示完成安装
  → 重启电脑

第 2 步：配置游戏音频
  → 右键任务栏音量图标 → 打开声音设置
  → 找到你的游戏
  → 将输出设备改为「CABLE Input」

第 3 步：启动程序
  → 双击运行「启动翻译助手.exe」
  → 开始游戏，享受实时翻译！

═══════════════════════════════════════════════════════════

💡 重要提示：

  • 首次运行会自动下载 AI 模型（约 1.5GB）
    请确保网络连接正常，下载需要 10-20 分钟

  • 建议游戏使用「无边框窗口」模式
    全屏模式可能会遮挡字幕

  • 配置文件位置：config/settings.yaml
    可以调整识别语言、翻译模式、字幕样式等

  • 日志文件位置：logs/app.log
    遇到问题时可以查看日志

═══════════════════════════════════════════════════════════

🔧 常见问题：

Q: 没有声音 / 识别不到语音？
A: 检查游戏音频是否输出到 CABLE Input
   右键音量图标 → 声音设置 → 应用音量和设备首选项

Q: 延迟太高？
A: 编辑 config/settings.yaml
   将 whisper.model_size 改为 "small"
   将 whisper.beam_size 改为 1

Q: 识别不准确？
A: 编辑 config/settings.yaml
   将 whisper.model_size 改为 "medium" 或 "large"
   确保游戏音量适中（不要太小或太大）

Q: 字幕被游戏遮挡？
A: 将游戏改为「无边框窗口」模式
   或编辑 config/settings.yaml 调整字幕位置

Q: 程序崩溃 / 报错？
A: 查看 logs/app.log 日志文件
   确保已安装虚拟声卡并重启电脑
   尝试重新下载模型

═══════════════════════════════════════════════════════════

📞 获取帮助：

  • 详细文档：docs/README.md
  • 快速开始：docs/QUICKSTART.md
  • 安装指南：docs/INSTALL.md

═══════════════════════════════════════════════════════════

⚠️  安全说明：

  本工具使用系统级音频捕获，不接触游戏进程
  不会导致封号，可以放心使用

  • 不注入游戏进程
  • 不修改游戏文件
  • 不读取游戏内存
  • 不 Hook 游戏函数

═══════════════════════════════════════════════════════════

📄 许可证：MIT License - 仅供个人学习使用

═══════════════════════════════════════════════════════════
"""

    with open(release_dir / "首次使用必读.txt", 'w', encoding='utf-8') as f:
        f.write(content)


def create_setup_wizard_bat(release_dir):
    """创建首次使用向导脚本"""
    content = """@echo off
chcp 65001 >nul
color 0A

echo ════════════════════════════════════════════════════════════
echo           游戏翻译助手 - 首次使用向导
echo ════════════════════════════════════════════════════════════
echo.
echo 本向导将帮助您安装虚拟声卡（必需组件）
echo.
echo 虚拟声卡用于捕获游戏音频，不会影响游戏性能
echo 安装过程需要管理员权限
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause

echo.
echo [1/3] 打开虚拟声卡下载页面...
echo.
echo 请在浏览器中下载 VBCABLE_Driver_Pack43.zip
echo 下载地址：https://vb-audio.com/Cable/
echo.
start https://vb-audio.com/Cable/
echo.
echo 下载完成后，请解压 zip 文件
echo.
pause

echo.
echo [2/3] 安装虚拟声卡
echo.
echo 请按照以下步骤操作：
echo 1. 找到解压后的文件夹
echo 2. 右键点击 VBCABLE_Setup_x64.exe
echo 3. 选择「以管理员身份运行」
echo 4. 点击「Install Driver」
echo 5. 等待安装完成
echo.
pause

echo.
echo [3/3] 完成安装
echo.
echo ════════════════════════════════════════════════════════════
echo           安装完成！
echo ════════════════════════════════════════════════════════════
echo.
echo 下一步：
echo 1. 重启电脑（重要！）
echo 2. 配置游戏音频输出到 CABLE Input
echo 3. 双击运行「启动翻译助手.exe」
echo.
echo 详细说明请查看「首次使用必读.txt」
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
"""

    with open(release_dir / "首次使用向导.bat", 'w', encoding='utf-8') as f:
        f.write(content)


def create_driver_link(release_dir):
    """创建虚拟声卡下载链接"""
    content = """[InternetShortcut]
URL=https://vb-audio.com/Cable/
"""

    with open(release_dir / "下载虚拟声卡.url", 'w', encoding='utf-8') as f:
        f.write(content)


def create_launcher_bat(release_dir):
    """创建启动脚本（用于目录模式）"""
    content = """@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" "app\启动翻译助手.exe"
"""

    with open(release_dir / "启动翻译助手.bat", 'w', encoding='utf-8') as f:
        f.write(content)


def get_file_size(file_path):
    """获取文件大小（人类可读格式）"""
    path = Path(file_path)
    if not path.exists():
        return "未知"

    size = path.stat().st_size

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

    return f"{size:.1f} TB"


if __name__ == '__main__':
    try:
        create_release()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n\n❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
