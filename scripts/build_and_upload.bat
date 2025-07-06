@echo off
REM Windows批处理脚本 - PyPI打包上传
REM 用于在Windows系统上运行PyPI打包上传脚本

echo Video2Text PyPI打包上传工具
echo ============================

REM 切换到脚本目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 显示菜单
echo.
echo 请选择操作:
echo 1. 清理构建文件
echo 2. 构建包
echo 3. 检查包
echo 4. 上传到TestPyPI
echo 5. 上传到PyPI
echo 6. 完整流程(清理+构建+检查+TestPyPI)
echo 7. 生产发布(清理+构建+检查+PyPI)
echo 8. 退出
echo.

set /p choice=请输入选项(1-8): 

if "%choice%"=="1" (
    python build_and_upload.py --clean
) else if "%choice%"=="2" (
    python build_and_upload.py --build
) else if "%choice%"=="3" (
    python build_and_upload.py --check
) else if "%choice%"=="4" (
    python build_and_upload.py --test-upload
) else if "%choice%"=="5" (
    python build_and_upload.py --upload
) else if "%choice%"=="6" (
    python build_and_upload.py --all
) else if "%choice%"=="7" (
    python build_and_upload.py --production
) else if "%choice%"=="8" (
    exit /b 0
) else (
    echo 无效选项
)

echo.
echo 操作完成，按任意键继续...
pause >nul 