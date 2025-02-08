import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from servefs.cli import app

runner = CliRunner()

def test_version():
    """测试版本信息显示"""
    result = runner.invoke(app, ["--version"], color=False)
    assert result.exit_code == 0
    assert "servefs version:" in result.stdout

def test_help():
    """测试帮助信息显示"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout

def test_invalid_port():
    """测试无效端口号"""
    result = runner.invoke(app, ["--port", "99999"], color=False)
    assert result.exit_code == 2
    assert "Invalid value for '--port'" in result.stdout
    assert "99999" in result.stdout

def test_invalid_root():
    """测试无效根目录"""
    result = runner.invoke(app, ["--root", "/nonexistent/path"], color=False)
    assert result.exit_code == 2
    for word in "Directory '/nonexistent/path' does not exist".split():
        assert word in result.stdout

@pytest.fixture
def temp_dir(tmp_path):
    """创建临时目录"""
    return tmp_path

def test_server_start(temp_dir):
    """测试服务器启动"""
    with patch("servefs.cli.uvicorn.run") as mock_run:
        result = runner.invoke(app, [
            "--root", str(temp_dir),
            "--port", "8888",
            "--host", "127.0.0.1",
            "--debug"
        ])
        
        assert result.exit_code == 0
        # 验证环境变量设置
        assert os.environ["SERVEFS_ROOT"] == str(temp_dir.absolute())
        assert os.environ["SERVEFS_DEBUG"] == "true"
        
        # 验证服务器启动参数
        mock_run.assert_called_once_with(
            "servefs.main:app",
            host="127.0.0.1",
            port=8888,
            log_level="info"
        )

def test_default_options():
    """测试默认选项"""
    with patch("servefs.cli.uvicorn.run") as mock_run:
        result = runner.invoke(app)
        
        assert result.exit_code == 0
        # 验证默认环境变量
        assert os.environ["SERVEFS_ROOT"] == str(Path(".").absolute())
        assert os.environ["SERVEFS_DEBUG"] == "false"
        
        # 验证默认服务器参数
        mock_run.assert_called_once_with(
            "servefs.main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )

def test_debug_mode():
    """测试调试模式"""
    with patch("servefs.cli.uvicorn.run") as mock_run:
        result = runner.invoke(app, ["--debug"])
        
        assert result.exit_code == 0
        assert os.environ["SERVEFS_DEBUG"] == "true"
        assert "Developer mode: enabled" in result.stdout
