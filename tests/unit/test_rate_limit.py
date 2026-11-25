"""
=============================================================================
اختبارات وحدوية لحدّ المعدل المشترك (sr_rate_limit.py + وسيلة sr_auth)
=============================================================================
التركيز على الضمانة الجديدة: الحدّ يبقى صحيحاً مع **عدة عمليات/عمال**،
لأن الحالة لم تعد في ذاكرة العملية الواحدة.
"""

import asyncio
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from sr_auth import Principal, SovereignRateLimitMiddleware
from sr_rate_limit import (
    BACKEND_MEMORY,
    BACKEND_SQLITE,
    MemoryRateLimitStore,
    SQLiteRateLimitStore,
    create_rate_limit_store,
)


class FakeClock:
    """ساعة يدوية لاختبار النافذة الزمنية دون انتظار."""

    def __init__(self, start: float = 1000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


# ==============================================================================
# 1. الخلفية في الذاكرة
# ==============================================================================
class TestMemoryStore:
    @pytest.fixture
    def clock(self):
        return FakeClock()

    @pytest.fixture
    def store(self, clock):
        return MemoryRateLimitStore(clock=clock)

    def test_allows_up_to_limit_then_rejects(self, store):
        for _ in range(3):
            allowed, retry = store.hit("general:60", "key:a", limit=3, window=60)
            assert allowed is True
            assert retry == 0

        allowed, retry = store.hit("general:60", "key:a", limit=3, window=60)
        assert allowed is False
        assert retry >= 1

    def test_window_slides_after_expiry(self, store, clock):
        for _ in range(2):
            store.hit("general:60", "key:a", limit=2, window=60)
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is False

        clock.advance(61)
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is True

    def test_retry_after_uses_oldest_hit(self, store, clock):
        for _ in range(2):
            store.hit("general:60", "key:a", limit=2, window=60)
        clock.advance(15)
        allowed, retry = store.hit("general:60", "key:a", limit=2, window=60)
        assert allowed is False
        assert 40 <= retry <= 46  # 60 - 15

    def test_identities_are_isolated(self, store):
        for _ in range(2):
            store.hit("general:60", "key:a", limit=2, window=60)
        assert store.hit("general:60", "key:b", limit=2, window=60)[0] is True

    def test_buckets_are_isolated(self, store):
        for _ in range(2):
            store.hit("chat:60", "key:a", limit=2, window=60)
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is True

    def test_reset_and_stats(self, store):
        store.hit("general:60", "key:a", limit=1, window=60)
        store.hit("general:60", "key:a", limit=1, window=60)
        stats = store.stats()
        assert stats["backend"] == BACKEND_MEMORY
        assert stats["shared_across_workers"] is False
        assert stats["accepted_total"] == 1
        assert stats["rejected_total"] == 1

        store.reset()
        assert store.stats()["tracked_hits"] == 0


# ==============================================================================
# 2. الخلفية المشتركة في SQLite (الضمانة متعددة العمال)
# ==============================================================================
class TestSQLiteStore:
    @pytest.fixture
    def clock(self):
        return FakeClock()

    @pytest.fixture
    def store(self, tmp_path, clock):
        instance = SQLiteRateLimitStore(tmp_path / "rl.db", clock=clock)
        yield instance
        instance.close()

    def test_allows_up_to_limit_then_rejects(self, store):
        for _ in range(3):
            assert store.hit("general:60", "key:a", limit=3, window=60)[0] is True
        allowed, retry = store.hit("general:60", "key:a", limit=3, window=60)
        assert allowed is False and retry >= 1

    def test_window_slides_after_expiry(self, store, clock):
        for _ in range(2):
            store.hit("general:60", "key:a", limit=2, window=60)
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is False

        clock.advance(61)
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is True

    def test_two_store_instances_share_the_same_counter(self, tmp_path, clock):
        """هذا هو جوهر الإصلاح: عاملان مختلفان لا يتضاعف الحدّ بينهما."""
        worker_a = SQLiteRateLimitStore(tmp_path / "shared.db", clock=clock)
        worker_b = SQLiteRateLimitStore(tmp_path / "shared.db", clock=clock)
        try:
            for _ in range(3):
                assert worker_a.hit("general:60", "key:a", limit=3, window=60)[0] is True
            # العامل الثاني يرى نفس الحالة ويطبّق نفس الحدّ
            allowed, retry = worker_b.hit("general:60", "key:a", limit=3, window=60)
            assert allowed is False
            assert retry >= 1
            # وهو مستقل عن هوية أخرى
            assert worker_b.hit("general:60", "key:b", limit=3, window=60)[0] is True
        finally:
            worker_a.close()
            worker_b.close()

    def test_state_survives_restart(self, tmp_path, clock):
        first = SQLiteRateLimitStore(tmp_path / "persist.db", clock=clock)
        first.hit("general:60", "key:a", limit=1, window=60)
        first.close()

        second = SQLiteRateLimitStore(tmp_path / "persist.db", clock=clock)
        try:
            assert second.hit("general:60", "key:a", limit=1, window=60)[0] is False
        finally:
            second.close()

    def test_same_instant_hits_are_all_counted(self, store):
        """الطابع الزمني المكرر لا يُسقط محاولة (المفتاح ليس ts)."""
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is True
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is True
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is False

    def test_stale_rows_are_cleaned(self, tmp_path, clock):
        store = SQLiteRateLimitStore(tmp_path / "clean.db", clock=clock, cleanup_every=1)
        try:
            store._conn.execute(
                "INSERT INTO rate_hits (bucket, identity, ts) VALUES (?, ?, ?)",
                ("general:60", "old-key", clock.now - 10_000),
            )
            store.hit("general:60", "key:a", limit=5, window=60)  # يفعّل التنظيف
            remaining = store._conn.execute(
                "SELECT COUNT(*) FROM rate_hits WHERE identity = 'old-key'"
            ).fetchone()[0]
            assert remaining == 0
        finally:
            store.close()

    def test_future_timestamps_do_not_lock_identity(self, store, clock):
        """قفزة ساعة للأمام ثم للخلف لا تُقفل الهوية إلى الأبد."""
        store.hit("general:60", "key:a", limit=2, window=60)
        store._conn.execute(
            "INSERT INTO rate_hits (bucket, identity, ts) VALUES (?, ?, ?)",
            ("general:60", "key:a", clock.now + 5_000),
        )
        clock.advance(1)
        assert store.hit("general:60", "key:a", limit=2, window=60)[0] is True

    def test_fail_open_when_database_is_unavailable(self, store):
        store._conn.close()  # يحاكي فقدان القرص/الملف أثناء التشغيل
        allowed, retry = store.hit("general:60", "key:a", limit=1, window=60)
        assert allowed is True
        assert retry == 0

    def test_schema_and_stats(self, store):
        store.hit("general:60", "key:a", limit=5, window=60)
        tables = {
            row[0]
            for row in store._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "rate_hits" in tables

        stats = store.stats()
        assert stats["backend"] == BACKEND_SQLITE
        assert stats["shared_across_workers"] is True
        assert stats["tracked_hits"] == 1
        assert stats["active_identities"] == 1
        assert stats["db_path"].endswith("rl.db")
        assert "\\" not in stats["db_path"] and "/" not in stats["db_path"]

    def test_reset_clears_counters(self, store):
        store.hit("general:60", "key:a", limit=1, window=60)
        store.reset()
        assert store.hit("general:60", "key:a", limit=1, window=60)[0] is True


# ==============================================================================
# 3. المصنع والتدرّج الآمن
# ==============================================================================
class TestStoreFactory:
    def test_explicit_memory_backend(self):
        store = create_rate_limit_store(BACKEND_MEMORY)
        assert isinstance(store, MemoryRateLimitStore)

    def test_default_uses_sqlite(self, tmp_path):
        store = create_rate_limit_store(db_path=str(tmp_path / "factory.db"))
        try:
            assert isinstance(store, SQLiteRateLimitStore)
        finally:
            store.close()

    def test_unknown_backend_falls_back_to_auto(self, tmp_path):
        store = create_rate_limit_store(backend="redis", db_path=str(tmp_path / "x.db"))
        try:
            assert isinstance(store, SQLiteRateLimitStore)
        finally:
            store.close()

    def test_unwritable_path_degrades_to_memory(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise sqlite3.OperationalError("unable to open database file")

        monkeypatch.setattr(sqlite3, "connect", _boom)
        store = create_rate_limit_store("sqlite", db_path="Z:/nowhere/rate.db")
        assert isinstance(store, MemoryRateLimitStore)


# ==============================================================================
# 4. الوسيلة: 429، الحزم المنفصلة، ومشاركة العمال
# ==============================================================================
class _DummyApp:
    """تطبيق ASGI مصغّر يسجّل مرات الاستدعاء."""

    def __init__(self):
        self.calls = 0

    async def __call__(self, scope, receive, send):
        self.calls += 1
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})


def _request(middleware, path="/api/rag/stats", method="GET", principal=None,
             ip="1.2.3.4", api_key=None):
    sent = []

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "path": path,
        "method": method,
        "headers": [(b"x-api-key", api_key.encode())] if api_key else [],
        "query_string": b"",
        "state": {"principal": principal} if principal else {},
        "client": (ip, 12345),
    }
    asyncio.run(middleware(scope, None, send))

    status = next((m["status"] for m in sent if m["type"] == "http.response.start"), None)
    headers = {}
    for message in sent:
        if message["type"] == "http.response.start":
            headers = {
                key.decode(): value.decode() for key, value in message.get("headers", [])
            }
    return status, headers


class TestRateLimitMiddleware:
    def test_returns_429_with_retry_after(self):
        app = _DummyApp()
        mw = SovereignRateLimitMiddleware(
            app, store=MemoryRateLimitStore(), general=(2, 60), chat=(1, 60)
        )
        assert _request(mw)[0] == 200
        assert _request(mw)[0] == 200
        status, headers = _request(mw)
        assert status == 429
        assert int(headers["retry-after"]) >= 1
        assert app.calls == 2

    def test_chat_bucket_is_separate_from_general(self):
        app = _DummyApp()
        mw = SovereignRateLimitMiddleware(
            app, store=MemoryRateLimitStore(), general=(5, 60), chat=(1, 60)
        )
        assert _request(mw, path="/api/chat", method="POST")[0] == 200
        assert _request(mw, path="/api/chat", method="POST")[0] == 429
        # الحدّ العام لم يُستهلك بعد
        assert _request(mw, path="/api/rag/stats")[0] == 200

    def test_separate_ips_are_metered_separately(self):
        mw = SovereignRateLimitMiddleware(
            _DummyApp(), store=MemoryRateLimitStore(), general=(1, 60), chat=(1, 60)
        )
        assert _request(mw, ip="10.0.0.1")[0] == 200
        assert _request(mw, ip="10.0.0.1")[0] == 429
        assert _request(mw, ip="10.0.0.2")[0] == 200

    def test_same_ip_shares_the_address_quota(self):
        """زائر خلف NAT لا يفتح حصة جديدة بتغيير المفتاح."""
        mw = SovereignRateLimitMiddleware(
            _DummyApp(), store=MemoryRateLimitStore(), general=(1, 60), chat=(1, 60),
            key_general=(100, 60), key_chat=(100, 60),
        )
        alice = Principal("alice", "client")
        bob = Principal("bob", "client")
        assert _request(mw, ip="10.0.0.5", principal=alice, api_key="sk-alice")[0] == 200
        assert _request(mw, ip="10.0.0.5", principal=bob, api_key="sk-bob")[0] == 429

    def test_credential_ceiling_caps_one_key_across_ips(self):
        """مفتاح واحد موزّع على عناوين كثيرة لا يتجاوز سقفه."""
        mw = SovereignRateLimitMiddleware(
            _DummyApp(), store=MemoryRateLimitStore(), general=(100, 60), chat=(100, 60),
            key_general=(2, 60), key_chat=(2, 60),
        )
        assert _request(mw, ip="10.0.0.1", api_key="sk-shared")[0] == 200
        assert _request(mw, ip="10.0.0.2", api_key="sk-shared")[0] == 200
        assert _request(mw, ip="10.0.0.3", api_key="sk-shared")[0] == 429
        # مفتاح آخر لا يتأثر بسقف الأول
        assert _request(mw, ip="10.0.0.4", api_key="sk-other")[0] == 200

    def test_no_key_uses_only_the_address_layer(self):
        mw = SovereignRateLimitMiddleware(
            _DummyApp(), store=MemoryRateLimitStore(), general=(1, 60), chat=(1, 60)
        )
        assert _request(mw, api_key=None)[0] == 200
        assert _request(mw, api_key=None)[0] == 429

    def test_options_preflight_is_not_counted(self):
        app = _DummyApp()
        mw = SovereignRateLimitMiddleware(
            app, store=MemoryRateLimitStore(), general=(1, 60), chat=(1, 60)
        )
        assert _request(mw, method="OPTIONS")[0] == 200
        assert _request(mw, method="OPTIONS")[0] == 200
        assert app.calls == 2

    def test_two_workers_sharing_one_store_enforce_one_limit(self):
        """يحاكي عاملين منفصلين: الحدّ الكلي يبقى 2 لا 4."""
        app = _DummyApp()
        shared = MemoryRateLimitStore()
        worker_a = SovereignRateLimitMiddleware(
            app, store=shared, general=(2, 60), chat=(1, 60)
        )
        worker_b = SovereignRateLimitMiddleware(
            app, store=shared, general=(2, 60), chat=(1, 60)
        )
        assert _request(worker_a)[0] == 200
        assert _request(worker_b)[0] == 200
        assert _request(worker_a)[0] == 429
        assert _request(worker_b)[0] == 429
