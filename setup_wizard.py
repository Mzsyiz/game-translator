#!/usr/bin/env python3
"""
智能安装向导 - 自动检测和安装所有依赖
"""
import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path


class SetupWizard:
    """安装向导"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_dir = self.base_dir / "venv"
        self.models_dir = self.base_dir / "models"

    def print_header(self, text):
        """打印标题"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60 + "\n")

    def print_step(self, step, total, text):
        """打印步骤"""
        print(f"[{step}/{total}] {text}...")

    def check_python(self):
        """检查 Python 版本"""
        self.print_step(1, 6, "检查 Python 环境")

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            print("❌ Python 版本过低，需要 3.10+")
            print("\n请访问 https://www.python.org/downloads/ 下载安装")
            input("\n按 Enter 退出...")
            sys.exit(1)

        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")

    def check_virtual_cable(self):
        """检查虚拟声卡"""
        self.print_step(2, 6, "检查虚拟声卡")

        try:
            import sounddevice as sd
            devices = sd.query_devices()

            has_cable = any("CABLE" in d['name'].upper() for d in devices)

            if not has_cable:
                print("⚠️  未检测到虚拟声卡")
                print("\n虚拟声卡是必需的，用于捕获游戏音频")
                print("\n请按照以下步骤安装：")
                print("1. 访问 https://vb-audio.com/Cable/")
                print("2. 下载 VBCABLE_Driver_Pack43.zip")
                print("3. 解压后右键 VBCABLE_Setup_x64.exe → 以管理员身份运行")
                print("4. 安装完成后重启电脑")

                choice = input("\n是否现在打开下载页面？(y/n): ")
                if choice.lower() == 'y':
                    import webbrowser
                    webbrowser.open("https://vb-audio.com/Cable/")

                input("\n安装完成后按 Enter 继续...")
                return False

            print("✓ 虚拟声卡已安装")
            return True

        except ImportError:
            print("⚠️  sounddevice 未安装，稍后将自动安装")
            return True

    def create_venv(self):
        """创建虚拟环境"""
        self.print_step(3, 6, "创建虚拟环境")

        if self.venv_dir.exists():
            print("✓ 虚拟环境已存在")
            return

        subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
        print("✓ 虚拟环境创建成功")

    def install_dependencies(self):
        """安装依赖"""
        self.print_step(4, 6, "安装 Python 依赖")

        # 获取 pip 路径
        if sys.platform == "win32":
            pip_path = self.venv_dir / "Scripts" / "pip.exe"
        else:
            pip_path = self.venv_dir / "bin" / "pip"

        # 升级 pip
        print("  升级 pip...")
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"],
                      check=True, capture_output=True)

        # 安装依赖
        print("  安装依赖包（这可能需要 5-10 分钟）...")
        requirements = self.base_dir / "requirements.txt"

        result = subprocess.run(
            [str(pip_path), "install", "-r", str(requirements)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ 安装失败：{result.stderr}")
            return False

        print("✓ 依赖安装成功")
        return True

    def download_models(self):
        """下载模型"""
        self.print_step(5, 6, "下载 AI 模型")

        print("  Whisper 模型将在首次运行时自动下载")
        print("  Argos 翻译模型下载中...")

        # 获取 python 路径
        if sys.platform == "win32":
            python_path = self.venv_dir / "Scripts" / "python.exe"
        else:
            python_path = self.venv_dir / "bin" / "python"

        script_path = self.base_dir / "scripts" / "download_models.py"

        try:
            subprocess.run([str(python_path), str(script_path)],
                          check=True, timeout=300)
            print("✓ 模型下载成功")
            return True
        except subprocess.TimeoutExpired:
            print("⚠️  下载超时，将在首次运行时继续下载")
            return True
        except Exception as e:
            print(f"⚠️  下载失败：{e}")
            print("  将在首次运行时自动下载")
            return True

    def create_shortcuts(self):
        """创建快捷方式"""
        self.print_step(6, 6, "创建快捷方式")

        # 创建启动脚本
        if sys.platform == "win32":
            python_path = self.venv_dir / "Scripts" / "python.exe"

            # 创建启动脚本
            start_script = self.base_dir / "启动翻译工具.bat"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{self.base_dir}"\n')
                f.write(f'"{python_path}" main.py\n')
                f.write(f'pause\n')

            # 创建测试脚本
            test_script = self.base_dir / "测试音频设备.bat"
            with open(test_script, 'w', encoding='utf-8') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{self.base_dir}"\n')
                f.write(f'"{python_path}" test_audio.py\n')
                f.write(f'pause\n')

            print("✓ 快捷方式创建成功")
            print(f"  - {start_script.name}")
            print(f"  - {test_script.name}")
        else:
            print("⚠️  非 Windows 系统，请手动运行 main.py")

    def run(self):
        """运行安装向导"""
        self.print_header("游戏实时翻译工具 - 安装向导")

        print("欢迎使用游戏实时翻译工具！")
        print("本向导将自动检测并安装所有必需组件\n")

        input("按 Enter 开始安装...")

        # 1. 检查 Python
        self.check_python()

        # 2. 检查虚拟声卡
        cable_ok = self.check_virtual_cable()
        if not cable_ok:
            print("\n⚠️  请先安装虚拟声卡，然后重新运行本安装程序")
            input("\n按 Enter 退出...")
            return

        # 3. 创建虚拟环境
        self.create_venv()

        # 4. 安装依赖
        if not self.install_dependencies():
            print("\n❌ 安装失败，请检查网络连接")
            input("\n按 Enter 退出...")
            return

        # 5. 下载模型
        self.download_models()

        # 6. 创建快捷方式
        self.create_shortcuts()

        # 完成
        self.print_header("安装完成！")

        print("✅ 所有组件安装成功！\n")
        print("下一步：")
        print("1. 配置游戏音频输出到虚拟声卡")
        print("   右键任务栏音量图标 → 声音设置")
        print("   将游戏输出改为 'CABLE Input'\n")
        print("2. 双击运行 '启动翻译工具.bat'\n")
        print("3. 开始游戏，享受实时翻译！\n")

        choice = input("是否现在打开配置文件？(y/n): ")
        if choice.lower() == 'y':
            config_file = self.base_dir / "config" / "settings.yaml"
            if sys.platform == "win32":
                os.startfile(config_file)
            else:
                subprocess.run(["open", str(config_file)])

        input("\n按 Enter 退出...")


if __name__ == "__main__":
    wizard = SetupWizard()
    try:
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n安装已取消")
    except Exception as e:
        print(f"\n\n❌ 安装出错：{e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 退出...")
