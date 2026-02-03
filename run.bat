@echo off
REM 游戏实时语音翻译工具 - 启动脚本

echo ========================================
echo 游戏实时语音翻译工具
echo ========================================
echo.

REM 检查虚拟环境
if exist venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，使用系统 Python
)

REM 检查依赖
echo 检查依赖...
python -c "import faster_whisper" 2>nul
if errorlevel 1 (
    echo 错误: 缺少依赖，请先运行 install.bat
    pause
    exit /b 1
)

REM 启动程序
echo.
echo 启动程序...
echo.
python main.py

pause
