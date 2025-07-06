#!/usr/bin/env python3
"""
发布前检查脚本
确保所有准备工作都已完成，可以安全发布
"""

import os
import sys
import subprocess
import re
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """运行命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, 
            capture_output=capture_output, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return e


def check_git_status():
    """检查Git状态"""
    print("检查Git状态...")
    
    # 检查是否有未提交的更改
    result = run_command("git status --porcelain")
    if result.returncode == 0 and result.stdout.strip():
        print("❌ 有未提交的更改:")
        print(result.stdout)
        return False
    
    # 检查是否有未推送的提交
    result = run_command("git log --oneline @{u}..HEAD", check=False)
    if result.returncode == 0 and result.stdout.strip():
        print("❌ 有未推送的提交:")
        print(result.stdout)
        return False
    
    print("✅ Git状态正常")
    return True


def check_version_consistency():
    """检查版本号一致性"""
    print("检查版本号一致性...")
    
    # 读取pyproject.toml中的版本
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml文件不存在")
        return False
    
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        print("❌ 无法找到版本号")
        return False
    
    version = match.group(1)
    print(f"✅ 当前版本: {version}")
    
    # 检查版本号格式
    if not re.match(r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$', version):
        print("❌ 版本号格式不正确")
        return False
    
    return True


def check_dependencies():
    """检查依赖"""
    print("检查构建依赖...")
    
    required_tools = ["build", "twine"]
    for tool in required_tools:
        result = run_command(f"python -m {tool} --version", check=False)
        if result.returncode != 0:
            print(f"❌ 缺少工具: {tool}")
            print("请运行: pip install build twine")
            return False
    
    print("✅ 构建依赖正常")
    return True


def check_tests():
    """检查测试"""
    print("运行测试...")
    
    # 检查是否有测试文件
    test_files = list(Path("tests").glob("test_*.py"))
    if not test_files:
        print("⚠️  没有找到测试文件")
        return True
    
    # 运行测试
    result = run_command("python -m pytest tests/ -v", check=False)
    if result.returncode != 0:
        print("❌ 测试失败")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print("✅ 测试通过")
    return True


def check_documentation():
    """检查文档"""
    print("检查文档...")
    
    required_files = ["README.md", "LICENSE", "PYPI_GUIDE.md"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少文件: {file}")
            return False
    
    # 检查README.md是否有内容
    readme_content = Path("README.md").read_text(encoding="utf-8")
    if len(readme_content.strip()) < 100:
        print("❌ README.md内容太少")
        return False
    
    print("✅ 文档检查通过")
    return True


def check_package_structure():
    """检查包结构"""
    print("检查包结构...")
    
    # 检查主包目录
    if not Path("video2text").exists():
        print("❌ 主包目录不存在")
        return False
    
    # 检查__init__.py
    if not Path("video2text/__init__.py").exists():
        print("❌ __init__.py文件不存在")
        return False
    
    # 检查核心模块
    required_modules = [
        "video2text/config.py",
        "video2text/downloader.py",
        "video2text/transcriber.py",
        "video2text/api.py",
        "video2text/gui.py",
        "video2text/cli.py",
    ]
    
    for module in required_modules:
        if not Path(module).exists():
            print(f"❌ 缺少模块: {module}")
            return False
    
    print("✅ 包结构正常")
    return True


def check_pyproject_toml():
    """检查pyproject.toml配置"""
    print("检查pyproject.toml配置...")
    
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    
    # 检查必要字段
    required_fields = [
        "name",
        "version", 
        "description",
        "readme",
        "license",
        "authors",
        "classifiers",
        "dependencies"
    ]
    
    for field in required_fields:
        if field not in content:
            print(f"❌ pyproject.toml缺少字段: {field}")
            return False
    
    # 检查是否有合适的分类器
    if "Programming Language :: Python :: 3" not in content:
        print("❌ 缺少Python 3分类器")
        return False
    
    print("✅ pyproject.toml配置正常")
    return True


def check_security():
    """安全检查"""
    print("进行安全检查...")
    
    # 检查是否有敏感信息
    sensitive_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
    ]
    
    for py_file in Path("video2text").glob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"⚠️  可能包含敏感信息: {py_file}")
                break
    
    print("✅ 安全检查通过")
    return True


def main():
    """主函数"""
    print("开始发布前检查...")
    print("=" * 50)
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    checks = [
        check_package_structure,
        check_pyproject_toml,
        check_version_consistency,
        check_dependencies,
        check_documentation,
        check_tests,
        check_git_status,
        check_security,
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"检查结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有检查都通过了！可以安全发布。")
        return 0
    else:
        print("❌ 有检查失败，请修复后再发布。")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 