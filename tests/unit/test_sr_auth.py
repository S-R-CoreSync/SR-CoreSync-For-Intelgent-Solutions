"""
=============================================================================
اختبارات وحدوية لوحدة المصادقة (sr_auth.py)
=============================================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from sr_auth import SovereignKeyStore, Principal, ROLE_ADMIN, ROLE_CLIENT


class TestSovereignKeyStore:
    """اختبارات لفئة مخزن المفاتيح السيادي."""

    def test_hash_key_returns_sha256(self):
        """يجب أن يُعيد تجزئة المفتاح بصيغة SHA-256."""
        store = SovereignKeyStore.__new__(SovereignKeyStore)
        digest = store.hash_key("test-key-123")
        assert len(digest) == 64  # SHA-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in digest)

    def test_hash_key_is_deterministic(self):
        """يجب أن تكون التجزئة محددة (نفس المدخل → نفس المخرج)."""
        store = SovereignKeyStore.__new__(SovereignKeyStore)
        d1 = store.hash_key("same-key")
        d2 = store.hash_key("same-key")
        assert d1 == d2

    def test_authenticate_valid_key(self):
        """يجب أن يُعاد هوية صالحة عند تقديم مفتاح صحيح."""
        store = SovereignKeyStore()
        # إضافة مفتاح تجريبي في الذاكرة فقط (بلا كتابة إلى الملف)
        store.add_key(name="test-user", plain_key="test-valid-key", role=ROLE_ADMIN, persist=False)

        principal = store.authenticate("test-valid-key")
        assert principal is not None
        assert principal.name == "test-user"
        assert principal.role == ROLE_ADMIN

    def test_authenticate_invalid_key(self):
        """يجب أن يُعاد None عند تقديم مفتاح خاطئ."""
        store = SovereignKeyStore()
        principal = store.authenticate("non-existent-key")
        assert principal is None

    def test_authenticate_empty_key(self):
        """يجب أن يُعاد None عند تقديم مفتاح فارغ."""
        store = SovereignKeyStore()
        principal = store.authenticate("")
        assert principal is None
        principal = store.authenticate(None)
        assert principal is None

    def test_extract_key_from_x_api_key_header(self):
        """يجب استخراج المفتاح من ترويسة X-API-Key."""
        store = SovereignKeyStore()
        headers = [(b"x-api-key", b"my-secret-key")]
        key = store.extract_key(headers, b"")
        assert key == "my-secret-key"

    def test_extract_key_from_bearer_authorization(self):
        """يجب استخراج المفتاح من ترويسة Authorization: Bearer."""
        store = SovereignKeyStore()
        headers = [(b"authorization", b"Bearer my-bearer-token")]
        key = store.extract_key(headers, b"")
        assert key == "my-bearer-token"

    def test_extract_key_from_query_string(self):
        """يجب استخراج المفتاح من سلسلة الاستعلام (لـ SSE)."""
        store = SovereignKeyStore()
        headers = []
        query_string = b"api_key=query-key-123"
        key = store.extract_key(headers, query_string)
        assert key == "query-key-123"

    def test_principal_is_admin_property(self):
        """يجب أن تعيد الخاصية is_admin القيمة الصحيحة للدور."""
        admin_principal = Principal("admin-user", ROLE_ADMIN)
        client_principal = Principal("client-user", ROLE_CLIENT)

        assert admin_principal.is_admin is True
        assert client_principal.is_admin is False

    def test_principal_invalid_role_defaults_to_client(self):
        """يجب أن يعتمد دور افتراضي (client) عند تمرير دور غير صالح."""
        principal = Principal("user", "invalid-role")
        assert principal.role == ROLE_CLIENT
        assert principal.is_admin is False


class TestKeyStoreWithEnvVars:
    """اختبارات لتحميل المفاتيح من متغيرات البيئة."""

    def test_load_keys_from_env(self, monkeypatch, tmp_path):
        """يجب تحميل المفاتيح من متغير البيئة CORESYNC_API_KEYS."""
        monkeypatch.setenv("CORESYNC_API_KEYS",
                           "env-admin:env-admin-key:admin,"
                           "env-client:env-client-key:client")

        store = SovereignKeyStore()
        assert store.auth_enabled is True

        # اختبار المفتاح الإداري
        principal = store.authenticate("env-admin-key")
        assert principal is not None
        assert principal.name == "env-admin"
        assert principal.role == ROLE_ADMIN

        # اختبار المفتاح العميل
        principal = store.authenticate("env-client-key")
        assert principal is not None
        assert principal.name == "env-client"
        assert principal.role == ROLE_CLIENT

    def test_auth_disabled_when_no_keys(self, monkeypatch, tmp_path):
        """يجب تعطيل المصادقة عندما لا توجد مفاتيح محددة (إغلاق افتراضي)."""
        monkeypatch.setenv("CORESYNC_API_KEYS", "")
        monkeypatch.setenv("CORESYNC_AUTH_FILE", str(tmp_path / "auth_keys.json"))

        store = SovereignKeyStore()
        assert store.auth_enabled is False
        assert len(store) == 0
        assert store.authenticate("any-key") is None