@echo off
chcp 65001 >nul
title Image Insight Pro Launcher
echo ========================================================
echo       Image Insight Pro - 智能影像数据分析工作台
echo ========================================================
echo.
echo [INFO] 正在初始化运行环境...

python "%~dp0app.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 程序异常退出 (Exit Code: %errorlevel%)
    echo 请检查是否安装了 python 并且已添加到环境变量。
    echo 推荐库: pip install pandas openpyxl pillow tkinterdnd2
    echo.
    pause
)
