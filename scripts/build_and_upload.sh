#!/bin/bash
# Linux/macOS shell脚本 - PyPI打包上传
# 用于在Unix系统上运行PyPI打包上传脚本

echo "Video2Text PyPI打包上传工具"
echo "============================"

# 切换到脚本目录
cd "$(dirname "$0")"

# 检查Python是否安装
if ! command -v python &> /dev/null; then
    echo "错误: Python未安装或不在PATH中"
    exit 1
fi

# 显示菜单
echo ""
echo "请选择操作:"
echo "1. 清理构建文件"
echo "2. 构建包"
echo "3. 检查包"
echo "4. 上传到TestPyPI"
echo "5. 上传到PyPI"
echo "6. 完整流程(清理+构建+检查+TestPyPI)"
echo "7. 生产发布(清理+构建+检查+PyPI)"
echo "8. 退出"
echo ""

read -p "请输入选项(1-8): " choice

case $choice in
    1)
        python build_and_upload.py --clean
        ;;
    2)
        python build_and_upload.py --build
        ;;
    3)
        python build_and_upload.py --check
        ;;
    4)
        python build_and_upload.py --test-upload
        ;;
    5)
        python build_and_upload.py --upload
        ;;
    6)
        python build_and_upload.py --all
        ;;
    7)
        python build_and_upload.py --production
        ;;
    8)
        exit 0
        ;;
    *)
        echo "无效选项"
        ;;
esac

echo ""
echo "操作完成，按Enter键继续..."
read 