@echo off
chcp 65001 >nul
title Image Optimizer Pro Launcher
echo ========================================================
echo       Image Optimizer Pro - 图片标准化处理工具
echo ========================================================
echo.
echo [INFO] 正在启动处理引擎...

python "%~dp0processor.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 程序异常退出 (Exit Code: %errorlevel%)
    echo 请检查是否安装了 python 并且已添加到环境变量。
    echo 推荐库: pip install pillow tkinterdnd2
    echo.
    pause
)
