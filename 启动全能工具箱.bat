@echo off
chcp 65001 >nul
title Image Toolkit Universal Launcher
echo ========================================================
echo       Image Toolkit Universal - 启动器
echo ========================================================
echo.
echo [INFO] 正在检查运行环境 (CustomTkinter)...

python -c "import customtkinter" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] 未检测到 customtkinter 库，正在自动安装...
    pip install customtkinter --index-url https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo [ERROR] 安装失败。请手动运行: pip install customtkinter
        pause
        exit /b
    )
    echo [SUCCESS] 安装完成！
)

echo [INFO] 启动全能工具箱...
echo.
python "%~dp0ImageToolkit_Universal.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 程序异常退出。
    pause
)
