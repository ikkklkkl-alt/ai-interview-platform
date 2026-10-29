"""测试环境准备：使用假配置，默认阻止真实模型请求。"""

import httpx
import pytest


@pytest.fixture(autouse=True)
def isolated_model_environment(monkeypatch):
    """每个测试开始时设置，测试结束后由 monkeypatch 自动恢复。"""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://example.invalid")
    monkeypatch.setenv("DEEPSEEK_MODEL", "test-model")

    def blocked_post(*args, **kwargs):
        pytest.fail("测试不应发真实请求，请先用 monkeypatch 替换 httpx.post")

    monkeypatch.setattr(httpx, "post", blocked_post)
