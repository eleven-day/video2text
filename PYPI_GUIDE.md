# PyPI打包上传指南

本指南详细说明如何将Video2Text项目打包并上传到PyPI。

## 前置要求

### 1. 安装必要工具

```bash
# 安装构建和上传工具
pip install build twine

# 或者使用项目依赖
pip install -e ".[dev]"
```

### 2. 注册PyPI账户

1. **PyPI正式版**: https://pypi.org/account/register/
2. **TestPyPI测试版**: https://test.pypi.org/account/register/

### 3. 配置API Token

#### 方法1: 环境变量(推荐)
```bash
# 设置TestPyPI token
export TESTPYPI_TOKEN="pypi-your-testpypi-token"

# 设置PyPI token
export PYPI_TOKEN="pypi-your-pypi-token"
```

#### 方法2: 配置文件
创建 `~/.pypirc` 文件:
```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-pypi-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token
```

## 使用脚本打包上传

### 方法1: 使用Python脚本(推荐)

```bash
# 查看帮助
python scripts/build_and_upload.py

# 完整流程(测试)
python scripts/build_and_upload.py --all

# 生产发布
python scripts/build_and_upload.py --production

# 单独操作
python scripts/build_and_upload.py --clean    # 清理
python scripts/build_and_upload.py --build    # 构建
python scripts/build_and_upload.py --check    # 检查
python scripts/build_and_upload.py --test-upload  # 上传到TestPyPI
python scripts/build_and_upload.py --upload   # 上传到PyPI
```

### 方法2: 使用系统脚本

#### Windows系统
```cmd
# 双击运行或命令行运行
scripts\build_and_upload.bat
```

#### Linux/macOS系统
```bash
# 运行脚本
./scripts/build_and_upload.sh
```

## 手动操作步骤

### 1. 清理构建文件

```bash
# 删除旧的构建文件
rm -rf build/ dist/ *.egg-info/
```

### 2. 更新版本号

编辑 `pyproject.toml` 文件，更新版本号:
```toml
[project]
name = "video2text"
version = "1.0.1"  # 更新版本号
```

### 3. 构建包

```bash
# 构建源码包和wheel包
python -m build
```

构建完成后，会在 `dist/` 目录生成:
- `video2text-1.0.1.tar.gz` (源码包)
- `video2text-1.0.1-py3-none-any.whl` (wheel包)

### 4. 检查包

```bash
# 检查包的完整性
python -m twine check dist/*
```

### 5. 测试上传(可选)

```bash
# 上传到TestPyPI进行测试
python -m twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ video2text
```

### 6. 正式上传

```bash
# 上传到PyPI
python -m twine upload dist/*
```

## 版本管理策略

### 语义化版本控制

遵循 [Semantic Versioning](https://semver.org/) 规范:
- `MAJOR.MINOR.PATCH` (例如: 1.2.3)
- `MAJOR`: 不兼容的API变更
- `MINOR`: 向后兼容的功能增加
- `PATCH`: 向后兼容的问题修复

### 版本号示例

```
1.0.0    # 首次发布
1.0.1    # 修复bug
1.1.0    # 添加新功能
2.0.0    # 重大变更
```

### 预发布版本

```
1.0.0a1  # Alpha版本
1.0.0b1  # Beta版本
1.0.0rc1 # Release Candidate
```

## 发布检查清单

### 发布前检查

- [ ] 代码已提交到git
- [ ] 版本号已更新
- [ ] CHANGELOG已更新
- [ ] 测试通过
- [ ] 文档已更新
- [ ] 依赖版本已确认

### 构建检查

- [ ] 清理旧的构建文件
- [ ] 构建成功
- [ ] 包完整性检查通过
- [ ] 在TestPyPI测试成功

### 发布后检查

- [ ] PyPI页面显示正常
- [ ] 可以正常安装
- [ ] 功能测试通过
- [ ] 创建git标签
- [ ] 发布说明已发布

## 常见问题

### 1. 构建失败

**问题**: `python -m build` 失败
**解决**: 
- 检查 `pyproject.toml` 配置
- 确保所有依赖已安装
- 检查文件结构是否正确

### 2. 上传失败

**问题**: `twine upload` 失败
**解决**:
- 检查API token是否正确
- 确保版本号未被使用
- 检查网络连接

### 3. 版本冲突

**问题**: 版本号已存在
**解决**:
- 更新版本号
- 清理并重新构建
- 不能覆盖已发布的版本

### 4. 依赖问题

**问题**: 安装后缺少依赖
**解决**:
- 检查 `pyproject.toml` 中的依赖配置
- 确保所有必要依赖都已列出
- 测试在干净环境中安装

## 自动化发布

### GitHub Actions

可以配置GitHub Actions自动发布:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## 维护建议

1. **定期更新**: 定期更新依赖和修复bug
2. **文档维护**: 保持文档与代码同步
3. **向后兼容**: 尽量保持API向后兼容
4. **安全更新**: 及时修复安全漏洞
5. **社区反馈**: 积极回应用户反馈和问题

## 参考资源

- [PyPI官方文档](https://packaging.python.org/)
- [Twine文档](https://twine.readthedocs.io/)
- [Python打包指南](https://packaging.python.org/tutorials/packaging-projects/)
- [语义化版本控制](https://semver.org/)

---

有任何问题，请查看项目的README.md或提交Issue。 