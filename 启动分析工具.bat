@echo off
chcp 936 >nul
title Image Insight Pro Launcher
echo [INFO] 正在初始化影像数据体检环境...

:: 读取配置文件中的 Python 路径
set "PYTHON_EXE="
if exist "%~dp0config.ini" (
    for /f "usebackq tokens=1* delims==" %%A in ("%~dp0config.ini") do (
        if /i "%%A"=="python_path" set "PYTHON_EXE=%%B"
    )
)

if not defined PYTHON_EXE (
    echo [Error] config.ini not found or python_path not set!
    pause
    exit /b
)

:: 确保环境完整
"%PYTHON_EXE%" -c "import pandas, openpyxl, PIL, tkinterdnd2" 2>nul
if %errorlevel% neq 0 (
    echo [提示] 正在安装报表引擎相关依赖...
    "%PYTHON_EXE%" -m pip install pandas openpyxl pillow tkinterdnd2 -i https://pypi.tuna.tsinghua.edu.cn/simple
)

"%PYTHON_EXE%" "%~dp0app.py"
if %errorlevel% neq 0 pause