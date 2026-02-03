@echo off
REM 游戏实时语音翻译工具 - 安装脚本

echo ========================================
echo 游戏实时语音翻译工具 - 安装向导
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] 创建虚拟环境...
if not exist venv (
    python -m venv venv
    echo 虚拟环境创建成功
) else (
    echo 虚拟环境已存在
)

echo.
echo [2/5] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [3/5] 升级 pip...
python -m pip install --upgrade pip

echo.
echo [4/5] 安装依赖包...
pip install -r requirements.txt

echo.
echo [5/5] 下载翻译模型...
python scripts\download_models.py

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 安装虚拟声卡 (VB-Audio Virtual Cable)
echo    下载: https://vb-audio.com/Cable/
echo.
echo 2. 配置游戏音频输出到虚拟声卡
echo.
echo 3. 运行 run.bat 启动程序
echo.
pause
