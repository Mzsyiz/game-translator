#!/usr/bin/env python3
"""
PyInstaller 打包脚本
将程序打包成独立的 exe 文件
"""
import sys
import shutil
from pathlib import Path


def build():
    """打包程序"""

    print("=" * 60)
    print("  游戏翻译助手 - 打包脚本")
    print("=" * 60)
    print()

    # 检查 PyInstaller
    try:
        import PyInstaller.__main__
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("\n请运行: pip install pyinstaller")
        sys.exit(1)

    print("[1/3] 清理旧文件...")

    # 清理旧的构建文件
    for dir_name in ['build', 'dist']:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✓ 删除 {dir_name}/")

    # 删除 spec 文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  ✓ 删除 {spec_file}")

    print("\n[2/3] 开始打包...")
    print("  这可能需要 5-10 分钟，请耐心等待...\n")

    # PyInstaller 参数
    args = [
        'main.py',

        # 基本设置
        '--name=启动翻译助手',
        '--onedir',                     # 改为目录模式（更稳定，构建更快）
        '--windowed',                   # 无控制台窗口
        '--noconfirm',                  # 覆盖输出目录

        # 图标（如果有）
        # '--icon=assets/icon.ico',

        # 添加数据文件
        '--add-data=config;config',
        '--add-data=translation/slang_dict.json;translation',

        # 隐藏导入（确保这些模块被包含）
        '--hidden-import=faster_whisper',
        '--hidden-import=argostranslate',
        '--hidden-import=torch',
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=sounddevice',
        '--hidden-import=webrtcvad',
        '--hidden-import=scipy',
        '--hidden-import=scipy.signal',
        '--hidden-import=numpy',
        '--hidden-import=loguru',
        '--hidden-import=yaml',
        '--hidden-import=deep_translator',
        '--hidden-import=pkg_resources.py2_warn',

        # 排除不需要的模块（减小体积）
        '--exclude-module=matplotlib',
        '--exclude-module=pandas',
        '--exclude-module=IPython',
        '--exclude-module=jupyter',
        '--exclude-module=notebook',
        '--exclude-module=tkinter',
        '--exclude-module=PIL',

        # 优化
        '--noupx',                      # 不使用 UPX 压缩（避免杀毒软件误报）

        # 日志级别
        '--log-level=WARN',             # 减少日志输出
    ]

    try:
        PyInstaller.__main__.run(args)
        print("\n[3/3] 打包完成！")

        # 检查输出目录
        dist_dir = Path('dist/启动翻译助手')
        exe_file = dist_dir / '启动翻译助手.exe'

        if exe_file.exists():
            print(f"\n✓ 可执行文件位置: {exe_file}")
            print(f"✓ 文件大小: {get_file_size(exe_file)}")
        else:
            print(f"\n⚠️  可执行文件未找到: {exe_file}")
            print("检查 dist/ 目录内容...")
            if dist_dir.exists():
                for item in dist_dir.iterdir():
                    print(f"  - {item.name}")

    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


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
        build()
    except KeyboardInterrupt:
        print("\n\n打包已取消")
        sys.exit(1)
