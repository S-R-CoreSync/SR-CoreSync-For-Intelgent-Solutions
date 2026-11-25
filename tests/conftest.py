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

# عزل ملف مفاتيح المصادقة: الاختبارات لا تلمس auth_keys.json الحقيقي في المستودع
_AUTH_TMP_DIR = Path(tempfile.mkdtemp(prefix="coresync_auth_"))
os.environ.setdefault("CORESYNC_AUTH_FILE", str(_AUTH_TMP_DIR / "auth_keys.json"))
os.environ.setdefault("CORESYNC_KEY_TTL_DAYS", "0")
# في الاختبارات: كل طلب يتحقق من بصمة الملف فوراً (سلوك الإنتاج: 0.25s)
os.environ.setdefault("CORESYNC_AUTH_RELOAD_INTERVAL", "0")

# عزل عدّادات حدّ المعدل أيضاً في مجلد مؤقت (لا ملفات تُنشأ داخل المستودع)
_RATE_TMP_DIR = Path(tempfile.mkdtemp(prefix="coresync_rl_"))
os.environ.setdefault("CORESYNC_RATE_LIMIT_DB", str(_RATE_TMP_DIR / "rate_limit.db"))

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
    """إنشاء دليل مؤقت للاختبارات مع ضمان إغلاق الاتصالات."""
    import gc
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)
        # إجبار garbage collection لإغلاق اتصالات SQLite قبل الحذف
        gc.collect()


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