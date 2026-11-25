"""
=============================================================================
اختبارات وحدوية لإدارة مفاتيح API المتقدمة والصلاحيات الدقيقة (sr_auth_advanced.py)
=============================================================================
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from sr_auth_advanced import (
    ALL_PERMISSIONS,
    ROLE_ADMIN,
    ROLE_CLIENT,
    ROLE_READONLY,
    ROLE_WRITER,
    ROLE_PERMISSIONS,
    AdvancedKeyEntry,
    AdvancedKeyStore,
    generate_api_key,
    hash_api_key,
    has_permission,
    mask_digest,
    parse_iso_utc,
    permissions_for_role,
    required_permission,
)
from sr_auth import Principal, SovereignKeyStore


def _iso(delta_days: float) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=delta_days)).isoformat()


@pytest.fixture
def store(tmp_path):
    """مخزن معزول بملف مؤقت وبلا مفاتيح بيئية."""
    return AdvancedKeyStore(auth_file=str(tmp_path / "auth_keys.json"), load_env=False)


class TestPermissionCatalog:
    """كتالوج الصلاحيات والأدوار."""

    def test_admin_holds_every_permission(self):
        assert set(permissions_for_role(ROLE_ADMIN)) == set(ALL_PERMISSIONS)

    def test_client_is_limited_to_conversation_and_reads(self):
        perms = permissions_for_role(ROLE_CLIENT)
        assert "chat:write" in perms
        assert "rag:read" in perms
        assert "admin:keys" not in perms
        assert "sessions:list" not in perms
        assert "appeals:write" not in perms

    def test_readonly_cannot_write(self):
        perms = permissions_for_role(ROLE_READONLY)
        assert "chat:read" in perms
        assert "chat:write" not in perms
        assert "rag:reindex" not in perms

    def test_writer_is_operational_not_administrative(self):
        perms = permissions_for_role(ROLE_WRITER)
        assert "upload:write" in perms
        assert "rag:write" in perms
        assert "rag:reindex" not in perms
        assert "admin:keys" not in perms

    def test_unknown_role_falls_back_to_client(self):
        assert permissions_for_role("superuser") == permissions_for_role(ROLE_CLIENT)
        assert permissions_for_role("") == permissions_for_role(ROLE_CLIENT)

    def test_has_permission_helper(self):
        assert has_permission(ROLE_ADMIN, "admin:system") is True
        assert has_permission(ROLE_CLIENT, "chat:write") is True
        assert has_permission(ROLE_CLIENT, "admin:keys") is False
        assert has_permission(ROLE_READONLY, "chat:write") is False

    def test_permissions_use_resource_action_shape(self):
        for permission in ALL_PERMISSIONS:
            resource, sep, action = permission.partition(":")
            assert sep == ":", permission
            assert resource and action, permission

    def test_permissions_serialisable_alias(self):
        from sr_auth_advanced import PERMISSIONS

        for role, perms in ROLE_PERMISSIONS.items():
            assert set(PERMISSIONS[role]) == set(perms)


class TestRoutePermissionMap:
    """خريطة المسارات → الصلاحيات."""

    @pytest.mark.parametrize("method,path,expected", [
        ("GET", "/api/rag/stats", "rag:read"),
        ("GET", "/api/rag/search", "rag:read"),
        ("GET", "/api/rag/cache/stats", "rag:read"),
        ("POST", "/api/chat", "chat:write"),
        ("GET", "/api/chat/stream", "chat:write"),
        ("POST", "/api/ai-concierge", "chat:write"),
        ("GET", "/api/sessions", "sessions:list"),
        ("GET", "/api/sessions/abc-123/history", "sessions:read"),
        ("DELETE", "/api/sessions/abc-123", "sessions:delete"),
        ("POST", "/api/rag/reindex", "rag:reindex"),
        ("DELETE", "/api/rag/cache", "rag:reindex"),
        ("POST", "/api/upload", "upload:write"),
        ("POST", "/api/events/publish", "events:publish"),
        ("GET", "/api/stream/events", "events:read"),
        ("GET", "/api/counsel/worm-verify", "appeals:read"),
        ("POST", "/api/appeals/lodge", "appeals:write"),
        ("POST", "/api/subagent/run-audit", "subagent:run"),
        ("GET", "/api/admin/keys", "admin:keys"),
        ("POST", "/api/admin/keys/abc123/revoke", "admin:keys"),
        ("WS", "/ws/chat", "chat:write"),
        ("WS", "/ws/events", "events:read"),
    ])
    def test_route_requires_expected_permission(self, method, path, expected):
        assert required_permission(method, path) == expected

    def test_unknown_route_requires_authentication_only(self):
        assert required_permission("GET", "/api/custom/thing") is None
        assert required_permission("GET", "/docs") is None

    def test_method_matters(self):
        # GET على مسار كتابة لا يُطابق قاعدة POST
        assert required_permission("GET", "/api/upload") is None

    def test_longest_prefix_wins(self):
        # /api/sessions/{id} لا يُخلط مع /api/sessions الإداري
        assert required_permission("GET", "/api/sessions") == "sessions:list"
        assert required_permission("GET", "/api/sessions/x/history") == "sessions:read"

    def test_case_insensitive_method(self):
        assert required_permission("post", "/api/chat") == "chat:write"


class TestKeyEntry:
    """سجل المفتاح الواحد."""

    def test_not_expired_without_timestamp(self):
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "a" * 64)
        assert entry.is_expired() is False
        assert entry.is_valid() is True

    def test_expired_when_timestamp_in_past(self):
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "a" * 64, expires_at=_iso(-1))
        assert entry.is_expired() is True
        assert entry.is_valid() is False

    def test_valid_when_timestamp_in_future(self):
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "a" * 64, expires_at=_iso(1))
        assert entry.is_expired() is False
        assert entry.seconds_until_expiry() > 0

    def test_naive_timestamp_is_treated_as_utc(self):
        naive = (datetime.now(timezone.utc) + timedelta(days=1)).replace(tzinfo=None).isoformat()
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "a" * 64, expires_at=naive)
        assert entry.is_expired() is False

    def test_malformed_timestamp_is_expired(self):
        """إغلاق افتراضي: تاريخ تالف لا يعني عمراً مفتوحاً."""
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "a" * 64, expires_at="not-a-date")
        assert entry.is_expired() is True
        assert entry.is_valid() is False

    def test_parse_iso_utc_helpers(self):
        assert parse_iso_utc(None) is None
        assert parse_iso_utc("") is None
        assert parse_iso_utc("bogus") is None
        assert parse_iso_utc("2026-11-25T10:00:00Z").tzinfo is not None

    def test_permission_override(self):
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "a" * 64, permissions=["rag:read"])
        assert entry.permission_set == frozenset({"rag:read"})
        assert entry.has_permission("rag:read") is True
        assert entry.has_permission("chat:write") is False

    def test_admin_always_has_permission(self):
        entry = AdvancedKeyEntry("k", ROLE_ADMIN, "a" * 64)
        assert entry.has_permission("admin:system") is True

    def test_record_usage(self):
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "a" * 64)
        entry.record_usage()
        entry.record_usage()
        assert entry.usage_count == 2
        assert entry.last_used_at is not None

    def test_public_dict_hides_secrets(self):
        entry = AdvancedKeyEntry("k", ROLE_CLIENT, "b" * 64)
        public = entry.to_public_dict()
        assert "plain_key" not in public
        assert public["key_masked"].endswith("bbbb")
        assert isinstance(public["permissions"], list)

    def test_to_dict_roundtrip(self):
        entry = AdvancedKeyEntry("k", ROLE_WRITER, "c" * 64, expires_at=_iso(2),
                                 permissions=["chat:read"], metadata={"env": "test"})
        restored = AdvancedKeyEntry.from_dict(entry.to_dict())
        assert restored.name == entry.name
        assert restored.role == entry.role
        assert restored.permissions == entry.permissions
        assert restored.metadata == {"env": "test"}


class TestAdvancedKeyStore:
    """دورة حياة المفاتيح: إنشاء، مصادقة، إلغاء، دوران، انتهاء."""

    def test_generated_key_is_random_and_prefixed(self):
        k1 = generate_api_key()
        k2 = generate_api_key()
        assert k1.startswith("sk_live_")
        assert k1 != k2
        assert len(k1) > 30

    def test_add_key_returns_plaintext_once_and_stores_hash(self, store, tmp_path):
        plain = store.add_key(name="svc-a", role=ROLE_CLIENT)
        assert len(store) == 1
        entry = store.get_entry(hash_api_key(plain))
        assert entry is not None
        assert plain not in (tmp_path / "auth_keys.json").read_text(encoding="utf-8")

    def test_authenticate_valid_and_invalid(self, store):
        plain = store.add_key(name="svc-a", role=ROLE_CLIENT)
        entry = store.authenticate(plain)
        assert entry is not None
        assert entry.name == "svc-a"
        assert store.authenticate("wrong-key") is None
        assert store.authenticate("") is None

    def test_key_persists_across_reload(self, store, tmp_path):
        plain = store.add_key(name="persisted", role=ROLE_WRITER, expires_in_days=30)
        reloaded = AdvancedKeyStore(auth_file=str(tmp_path / "auth_keys.json"), load_env=False)
        entry = reloaded.authenticate(plain)
        assert entry is not None
        assert entry.role == ROLE_WRITER
        assert entry.expires_at is not None

    def test_duplicate_key_rejected(self, store):
        store.add_key(name="a", plain_key="sk-fixed-value")
        with pytest.raises(ValueError):
            store.add_key(name="b", plain_key="sk-fixed-value")

    def test_unknown_role_rejected(self, store):
        with pytest.raises(ValueError):
            store.add_key(name="a", role="root")

    def test_unknown_permission_rejected(self, store):
        with pytest.raises(ValueError):
            store.add_key(name="a", permissions=["chat:destroy"])

    def test_empty_permission_list_rejected(self, store):
        with pytest.raises(ValueError):
            store.add_key(name="a", permissions=[])

    def test_blank_name_rejected(self, store):
        with pytest.raises(ValueError):
            store.add_key(name="   ")

    def test_non_positive_expiry_rejected(self, store):
        with pytest.raises(ValueError):
            store.add_key(name="a", expires_in_days=0)
        with pytest.raises(ValueError):
            store.add_key(name="b", expires_in_days=-5)

    def test_expired_key_is_rejected(self, store):
        plain = store.add_key(name="short-lived", expires_in_days=1)
        store.get_entry(hash_api_key(plain)).expires_at = _iso(-0.01)
        assert store.authenticate(plain) is None

    def test_revoked_key_is_rejected(self, store):
        plain = store.add_key(name="to-revoke")
        digest = hash_api_key(plain)
        assert store.revoke_key(digest) is True
        assert store.authenticate(plain) is None
        assert store.revoke_key("f" * 64) is False

    def test_revoke_by_name(self, store):
        store.add_key(name="dup")
        store.add_key(name="dup")
        assert store.revoke_by_name("dup") == 2

    def test_rotate_replaces_key_and_keeps_policy(self, store):
        old_plain = store.add_key(name="rotating", role=ROLE_WRITER,
                                  expires_in_days=10, permissions=["rag:read", "chat:read"])
        old_digest = hash_api_key(old_plain)
        new_plain = store.rotate_key(old_digest)

        assert new_plain and new_plain != old_plain
        assert store.authenticate(old_plain) is None
        entry = store.authenticate(new_plain)
        assert entry is not None
        assert entry.name == "rotating"
        assert entry.role == ROLE_WRITER
        assert entry.permission_set == frozenset({"rag:read", "chat:read"})
        assert "rotated_from" in entry.metadata

    def test_rotate_missing_key_returns_none(self, store):
        assert store.rotate_key("a" * 64) is None

    def test_rotate_revoked_key_raises(self, store):
        plain = store.add_key(name="dead")
        digest = hash_api_key(plain)
        store.revoke_key(digest)
        with pytest.raises(ValueError):
            store.rotate_key(digest)

    def test_usage_is_buffered_until_flush(self, store, tmp_path):
        plain = store.add_key(name="counted")
        digest = hash_api_key(plain)
        store.authenticate(plain)
        store.authenticate(plain)

        assert store.get_entry(digest).usage_count == 2
        assert store.stats()["pending_usage_flush"] is True
        # لم تُكتب عدادات الاستخدام إلى القرص بعد (لا كتابة في مسار المصادقة)
        on_disk = (tmp_path / "auth_keys.json").read_text(encoding="utf-8")
        assert '"usage_count": 0' in on_disk

        assert store.flush_usage() is True
        flushed = (tmp_path / "auth_keys.json").read_text(encoding="utf-8")
        assert '"usage_count": 2' in flushed

    def test_purge_expired(self, store):
        plain = store.add_key(name="short", expires_in_days=1)
        store.get_entry(hash_api_key(plain)).expires_at = _iso(-1)
        store.add_key(name="healthy", expires_in_days=5)
        assert store.purge_expired() == 1
        assert len(store) == 1

    def test_list_keys_is_safe(self, store):
        plain = store.add_key(name="listed", role=ROLE_CLIENT)
        keys = store.list_keys()
        assert len(keys) == 1
        assert keys[0]["name"] == "listed"
        assert "plain_key" not in keys[0]
        assert plain not in str(keys)

    def test_stats_counts(self, store):
        store.add_key(name="a", role=ROLE_CLIENT)
        revoked = store.add_key(name="b", role=ROLE_CLIENT)
        store.revoke_key(hash_api_key(revoked))
        stats = store.stats()
        assert stats["total_keys"] == 2
        assert stats["valid_keys"] == 1
        assert stats["revoked_keys"] == 1
        assert stats["roles"][ROLE_CLIENT] == 2

    def test_env_keys_are_loaded(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CORESYNC_API_KEYS", "env-svc:env-secret:readonly")
        store = AdvancedKeyStore(auth_file=str(tmp_path / "none.json"))
        entry = store.authenticate("env-secret")
        assert entry is not None
        assert entry.role == ROLE_READONLY
        assert entry.has_permission("chat:write") is False

    def test_unknown_role_in_env_falls_back_to_client(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CORESYNC_API_KEYS", "env-svc:env-secret-2:superuser")
        store = AdvancedKeyStore(auth_file=str(tmp_path / "none.json"))
        entry = store.authenticate("env-secret-2")
        assert entry is not None
        assert entry.role == ROLE_CLIENT

    def test_masking_helper(self):
        digest = "a" * 60 + "1234"
        masked = mask_digest(digest)
        assert masked.startswith("a" * 12)
        assert masked.endswith("1234")
        assert len(masked) < len(digest)


class TestSovereignKeyStoreFacade:
    """واجهة sr_auth فوق المخزن المتقدم (Principal + الصلاحيات)."""

    def test_authenticate_returns_principal_with_permissions(self, tmp_path):
        store = SovereignKeyStore(auth_file=str(tmp_path / "auth_keys.json"))
        plain = store.add_key(name="facade", role=ROLE_WRITER)
        principal = store.authenticate(plain)
        assert isinstance(principal, Principal)
        assert principal.name == "facade"
        assert principal.has("upload:write") is True
        assert principal.has("admin:keys") is False

    def test_permission_override_reaches_principal(self, tmp_path):
        store = SovereignKeyStore(auth_file=str(tmp_path / "auth_keys.json"))
        plain = store.add_key(name="scoped", role=ROLE_CLIENT, permissions=["rag:read"])
        principal = store.authenticate(plain)
        assert principal.permissions == frozenset({"rag:read"})
        assert principal.has("chat:write") is False

    def test_admin_principal_has_wildcard_access(self, tmp_path):
        store = SovereignKeyStore(auth_file=str(tmp_path / "auth_keys.json"))
        plain = store.add_key(name="root", role=ROLE_ADMIN)
        principal = store.authenticate(plain)
        assert principal.is_admin is True
        assert principal.has("admin:system") is True
        assert principal.has("anything:new") is True

    def test_revocation_blocks_principal(self, tmp_path):
        store = SovereignKeyStore(auth_file=str(tmp_path / "auth_keys.json"))
        plain = store.add_key(name="tmp", role=ROLE_CLIENT)
        store.revoke_key(store.hash_key(plain))
        assert store.authenticate(plain) is None

    def test_principal_as_dict_exposes_scopes(self):
        principal = Principal("svc", ROLE_READONLY)
        payload = principal.as_dict()
        assert payload["role"] == ROLE_READONLY
        assert "rag:read" in payload["permissions"]


class FakeMonotonic:
    """ساعة يدوية لاختبار كبح إعادة التحميل."""

    def __init__(self, start: float = 1000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class TestCrossWorkerCoherence:
    """عاملان على نفس الملف: الإدارة من أحدهما تسري على الآخر بلا إعادة تشغيل."""

    @pytest.fixture
    def stores(self, tmp_path):
        path = str(tmp_path / "keys.json")
        worker_a = AdvancedKeyStore(auth_file=path, load_env=False, reload_interval=0.0)
        worker_b = AdvancedKeyStore(auth_file=path, load_env=False, reload_interval=0.0)
        return worker_a, worker_b

    def test_key_added_by_one_worker_is_valid_on_the_other(self, stores):
        worker_a, worker_b = stores
        plain = worker_a.add_key(name="shared-new", role=ROLE_CLIENT)
        assert worker_b.authenticate(plain) is not None

    def test_revocation_reaches_the_other_worker(self, stores):
        worker_a, worker_b = stores
        plain = worker_a.add_key(name="to-kill", role=ROLE_CLIENT)
        assert worker_b.authenticate(plain) is not None

        worker_a.revoke_key(hash_api_key(plain))
        assert worker_b.authenticate(plain) is None

    def test_rotation_reaches_the_other_worker(self, stores):
        worker_a, worker_b = stores
        old_plain = worker_a.add_key(name="rotating", role=ROLE_WRITER)
        new_plain = worker_a.rotate_key(hash_api_key(old_plain))

        assert worker_b.authenticate(old_plain) is None
        entry = worker_b.authenticate(new_plain)
        assert entry is not None and entry.name == "rotating"

    def test_no_lost_update_between_workers(self, stores):
        """كتابة عامل لا تمحو مفتاحاً أضافه الآخر (read-modify-write)."""
        worker_a, worker_b = stores
        key_a = worker_a.add_key(name="from-a", role=ROLE_CLIENT)
        key_b = worker_b.add_key(name="from-b", role=ROLE_CLIENT)

        fresh = AdvancedKeyStore(auth_file=str(worker_a.auth_file), load_env=False)
        assert fresh.authenticate(key_a) is not None
        assert fresh.authenticate(key_b) is not None

    def test_usage_counters_survive_reload(self, stores):
        worker_a, worker_b = stores
        plain = worker_a.add_key(name="counted", role=ROLE_CLIENT)
        digest = hash_api_key(plain)

        worker_b.authenticate(plain)
        worker_b.authenticate(plain)

        worker_a.add_key(name="forces-reload", role=ROLE_CLIENT)
        assert worker_b.reload_if_changed(force=True) is True
        assert worker_b.get_entry(digest).usage_count == 2

    def test_volatile_keys_survive_external_reload(self, stores):
        worker_a, worker_b = stores
        ephemeral = worker_a.add_key(name="ephemeral", role=ROLE_CLIENT, persist=False)
        assert worker_b.authenticate(ephemeral) is None  # لم يُكتب إلى الملف

        worker_b.add_key(name="durable", role=ROLE_CLIENT)  # عامل آخر يغيّر الملف
        assert worker_a.reload_if_changed(force=True) is True
        assert worker_a.authenticate(ephemeral) is not None

    def test_reload_is_throttled_then_allowed(self, tmp_path):
        clock = FakeMonotonic()
        path = str(tmp_path / "throttle.json")
        writer = AdvancedKeyStore(auth_file=path, load_env=False)
        reader = AdvancedKeyStore(auth_file=path, load_env=False,
                                  reload_interval=5.0, clock=clock)

        plain = writer.add_key(name="late", role=ROLE_CLIENT)
        assert reader.reload_if_changed() is True          # أول فحص مسموح دائماً
        clock.advance(1)
        assert reader.reload_if_changed() is False         # داخل المهلة

        writer.add_key(name="later", role=ROLE_CLIENT)
        assert reader.reload_if_changed() is False         # ما زال داخل المهلة
        clock.advance(10)
        assert reader.reload_if_changed() is True          # انتهت المهلة وملف متغيّر
        assert reader.authenticate(plain) is not None

    def test_no_reload_when_file_unchanged(self, stores):
        worker_a, worker_b = stores
        worker_a.add_key(name="stable", role=ROLE_CLIENT)
        assert worker_b.reload_if_changed(force=True) is True
        assert worker_b.reload_if_changed(force=True) is False
