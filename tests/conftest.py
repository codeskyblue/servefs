import os
import pytest

@pytest.fixture(autouse=True)
def clean_env():
    """清理测试环境变量"""
    # 备份现有环境变量
    old_env = {}
    for key in ["SERVEFS_ROOT", "SERVEFS_DEBUG"]:
        if key in os.environ:
            old_env[key] = os.environ[key]
            del os.environ[key]
    
    yield
    
    # 恢复环境变量
    for key, value in old_env.items():
        os.environ[key] = value
