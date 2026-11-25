"""
=============================================================================
S&R CoreSync — إعداداتpytest والتجهيزات المشتركة (Fixtures)
=============================================================================
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# إضافة جذر المشروع إلى المسار
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ضبط الترميز للعربية
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest


@pytest.fixture(scope="session")
def project_root():
    """إرجاع مسار جذر المشروع."""
    return PROJECT_ROOT


@pytest.fixture
def temp_dir():
    """إنشاء دليل مؤقت للاختبارات."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def mock_env(monkeypatch):
    """تعيين متغيرات بيئة مؤقتة للاختبار."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-dummy-key-12345")
    monkeypatch.setenv("CORESYNC_API_KEYS",
                       "admin-test:sk-admin-secret-123:admin,"
                       "client-test:sk-client-secret-456:client")
    monkeypatch.setenv("CORESYNC_AUTH_DISABLED", "0")
    monkeypatch.setenv("CORESYNC_RATE_LIMIT", "1000/min")
    monkeypatch.setenv("CORESYNC_CHAT_RATE_LIMIT", "100/min")


@pytest.fixture
def sample_api_keys():
    """عينة من مفاتيح API للاختبار."""
    return {
        "admin": "sk-admin-secret-123",
        "client": "sk-client-secret-456",
        "invalid": "sk-invalid-key"
    }