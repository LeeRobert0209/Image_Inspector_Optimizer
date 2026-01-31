@echo off
chcp 936 >nul
title Image Toolkit Universal Launcher - Alicia
echo ========================================================
echo       Image Toolkit Universal - 旗舰全能版启动器
echo ========================================================

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

:: 检查并自动安装特有的 UI 库
echo [环境检查] 正在验证 CustomTkinter 库...
"%PYTHON_EXE%" -c "import customtkinter" 2>nul
if %errorlevel% neq 0 (
    echo [自动补全] 正在安装现代 UI 组件...
    "%PYTHON_EXE%" -m pip install customtkinter -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo [启动中] 正在开启全能影像工作站...
"%PYTHON_EXE%" "%~dp0ImageToolkit_Universal.py"
if %errorlevel% neq 0 pause