@echo off
chcp 936 >nul
title Image Optimizer Pro Launcher
echo [INFO] 正在启动标准化处理管线...

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

"%PYTHON_EXE%" "%~dp0processor.py"
if %errorlevel% neq 0 pause