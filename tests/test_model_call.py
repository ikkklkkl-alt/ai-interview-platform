"""Day 5 第三、四关：使用模拟响应测试调用流程。"""

import json

import httpx
import pytest

from scripts import structured_question


def test_main_prints_valid_question(monkeypatch, capsys):
    pytest.skip("待完成第三关：替换 httpx.post，验证成功输出")
    # TODO：构造完整响应，替换外部请求，调用 main 并检查打印结果。


def test_main_rejects_invalid_json(monkeypatch, capsys):
    pytest.skip("待完成第四关：验证模型正文不是 JSON 时提示并退出")
    # TODO：外层响应合法，finish_reason 为 stop，content 使用普通文字。


def test_main_rejects_truncated_response(monkeypatch, capsys):
    pytest.skip("待完成第四关：验证 length 结束时拒绝继续使用结果")
    # TODO：使用完整的 JSON 正文，但将 finish_reason 设为 length。
