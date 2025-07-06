#!/usr/bin/env python3
"""
PyPI打包上传脚本
用于将video2text项目打包并上传到PyPI
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并处理错误"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    
    # 要清理的目录和文件
    clean_targets = [
        "build",
        "dist",
        "*.egg-info",
        "__pycache__",
        "video2text/__pycache__",
        "video2text/*.pyc",
        "tests/__pycache__",
        "tests/*.pyc"
    ]
    
    for target in clean_targets:
        if "*" in target:
            # 使用glob匹配
            import glob
            for path in glob.glob(target):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"删除目录: {path}")
                else:
                    os.remove(path)
                    print(f"删除文件: {path}")
        else:
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.rmtree(target)
                    print(f"删除目录: {target}")
                else:
                    os.remove(target)
                    print(f"删除文件: {target}")


def check_requirements():
    """检查必要的工具是否安装"""
    print("检查必要工具...")
    
    required_tools = ["build", "twine"]
    missing_tools = []
    
    for tool in required_tools:
        result = run_command(f"python -m {tool} --version", check=False)
        if result.returncode != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"缺少必要工具: {missing_tools}")
        print("请运行以下命令安装:")
        print("pip install build twine")
        sys.exit(1)
    
    print("所有必要工具已安装")


def build_package():
    """构建包"""
    print("构建包...")
    
    # 构建源码包和wheel包
    run_command("python -m build")
    
    # 检查构建结果
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("构建失败: dist目录不存在")
        sys.exit(1)
    
    files = list(dist_dir.glob("*"))
    if not files:
        print("构建失败: dist目录为空")
        sys.exit(1)
    
    print("构建成功，生成文件:")
    for file in files:
        print(f"  - {file.name}")


def check_package():
    """检查包的完整性"""
    print("检查包完整性...")
    
    # 使用twine检查包
    run_command("python -m twine check dist/*")
    print("包检查通过")


def upload_to_testpypi():
    """上传到TestPyPI"""
    print("上传到TestPyPI...")
    
    # 检查是否有TestPyPI token
    if not os.getenv("TESTPYPI_TOKEN"):
        print("警告: 未设置TESTPYPI_TOKEN环境变量")
        print("请设置TestPyPI API token或手动输入用户名密码")
    
    run_command("python -m twine upload --repository testpypi dist/*")
    print("上传到TestPyPI成功")


def upload_to_pypi():
    """上传到PyPI"""
    print("上传到PyPI...")
    
    # 检查是否有PyPI token
    if not os.getenv("PYPI_TOKEN"):
        print("警告: 未设置PYPI_TOKEN环境变量")
        print("请设置PyPI API token或手动输入用户名密码")
    
    # 确认上传
    response = input("确认上传到PyPI? (y/N): ")
    if response.lower() != 'y':
        print("取消上传")
        return
    
    run_command("python -m twine upload dist/*")
    print("上传到PyPI成功")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PyPI打包上传工具")
    parser.add_argument("--clean", action="store_true", help="清理构建文件")
    parser.add_argument("--build", action="store_true", help="构建包")
    parser.add_argument("--check", action="store_true", help="检查包")
    parser.add_argument("--test-upload", action="store_true", help="上传到TestPyPI")
    parser.add_argument("--upload", action="store_true", help="上传到PyPI")
    parser.add_argument("--all", action="store_true", help="执行完整流程(清理+构建+检查+TestPyPI)")
    parser.add_argument("--production", action="store_true", help="生产发布(清理+构建+检查+PyPI)")
    
    args = parser.parse_args()
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查必要工具
    check_requirements()
    
    if args.all:
        # 完整流程
        clean_build()
        build_package()
        check_package()
        upload_to_testpypi()
    elif args.production:
        # 生产发布
        clean_build()
        build_package()
        check_package()
        upload_to_pypi()
    else:
        # 单独操作
        if args.clean:
            clean_build()
        if args.build:
            build_package()
        if args.check:
            check_package()
        if args.test_upload:
            upload_to_testpypi()
        if args.upload:
            upload_to_pypi()
        
        # 如果没有指定任何操作，显示帮助
        if not any([args.clean, args.build, args.check, args.test_upload, args.upload]):
            parser.print_help()


if __name__ == "__main__":
    main() 