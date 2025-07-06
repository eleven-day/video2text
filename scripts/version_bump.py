#!/usr/bin/env python3
"""
版本管理脚本
用于自动更新pyproject.toml中的版本号
"""

import re
import sys
import argparse
from pathlib import Path


def read_version():
    """读取当前版本号"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("错误: pyproject.toml文件不存在")
        sys.exit(1)
    
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        print("错误: 无法找到版本号")
        sys.exit(1)
    
    return match.group(1)


def write_version(new_version):
    """写入新版本号"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    
    # 替换版本号
    new_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject_path.write_text(new_content, encoding="utf-8")
    print(f"版本号已更新为: {new_version}")


def parse_version(version_str):
    """解析版本号"""
    # 支持语义化版本号: major.minor.patch
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9]+))?$', version_str)
    if not match:
        raise ValueError(f"无效的版本号格式: {version_str}")
    
    major, minor, patch, pre = match.groups()
    return int(major), int(minor), int(patch), pre


def format_version(major, minor, patch, pre=None):
    """格式化版本号"""
    version = f"{major}.{minor}.{patch}"
    if pre:
        version += f"-{pre}"
    return version


def bump_version(current_version, bump_type):
    """增加版本号"""
    try:
        major, minor, patch, pre = parse_version(current_version)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
        pre = None
    elif bump_type == "minor":
        minor += 1
        patch = 0
        pre = None
    elif bump_type == "patch":
        patch += 1
        pre = None
    else:
        print(f"错误: 不支持的版本类型: {bump_type}")
        sys.exit(1)
    
    return format_version(major, minor, patch, pre)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="版本管理工具")
    parser.add_argument("--show", action="store_true", help="显示当前版本")
    parser.add_argument("--set", metavar="VERSION", help="设置指定版本")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], 
                       help="增加版本号 (major/minor/patch)")
    
    args = parser.parse_args()
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    import os
    os.chdir(project_dir)
    
    current_version = read_version()
    
    if args.show:
        print(f"当前版本: {current_version}")
    elif args.set:
        # 验证版本号格式
        try:
            parse_version(args.set)
            write_version(args.set)
        except ValueError as e:
            print(f"错误: {e}")
            sys.exit(1)
    elif args.bump:
        new_version = bump_version(current_version, args.bump)
        print(f"版本号从 {current_version} 更新到 {new_version}")
        write_version(new_version)
    else:
        # 显示当前版本和帮助
        print(f"当前版本: {current_version}")
        print()
        parser.print_help()


if __name__ == "__main__":
    main() 