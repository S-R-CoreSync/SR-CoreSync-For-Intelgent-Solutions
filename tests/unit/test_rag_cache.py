"""
=============================================================================
اختبارات وحدوية لطبقة التخزين المؤقت لاستعلامات RAG (sr_rag_engine.QueryCache)
=============================================================================
"""

import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from sr_rag_engine import (
    QueryCache,
    SovereignRAGDatabase,
    reset_query_caches,
)


class FakeClock:
    """ساعة يدوية لاختبار TTL دون انتظار حقيقي."""

    def __init__(self, start: float = 1000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def cache():
    return QueryCache(ttl_seconds=60.0, max_entries=4, namespace="test", clock=FakeClock())


class TestFingerprint:
    """بصمة الاستعلام."""

    def test_stable_for_same_query(self, cache):
        assert cache.fingerprint("التحكيم التجاري") == cache.fingerprint("التحكيم التجاري")

    def test_normalises_arabic_and_spacing(self, cache):
        # تطبيع الألف/المسافات يجب أن يجمع الاستعلامين على بصمة واحدة
        assert cache.fingerprint("إحكام  تجاري") == cache.fingerprint("احكام تجاري")

    def test_differs_by_top_k(self, cache):
        assert cache.fingerprint("q", top_k=2) != cache.fingerprint("q", top_k=4)

    def test_differs_by_alpha(self, cache):
        assert cache.fingerprint("q", alpha=0.55) != cache.fingerprint("q", alpha=0.80)

    def test_differs_by_namespace(self):
        a = QueryCache(ttl_seconds=10, namespace="db-a", clock=FakeClock())
        b = QueryCache(ttl_seconds=10, namespace="db-b", clock=FakeClock())
        assert a.fingerprint("q") != b.fingerprint("q")

    def test_changes_after_invalidation(self, cache):
        key_before = cache.fingerprint("q")
        cache.invalidate()
        assert cache.fingerprint("q") != key_before


class TestCacheBehaviour:
    """التخزين، TTL، LRU، الإبطال، الإحصاءات."""

    def test_miss_then_hit(self, cache):
        key = cache.fingerprint("q")
        assert cache.get(key) is None
        cache.set(key, [{"id": 1}])
        assert cache.get(key) == [{"id": 1}]
        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["stores"] == 1

    def test_ttl_expiry(self):
        clock = FakeClock()
        cache = QueryCache(ttl_seconds=30, max_entries=4, clock=clock)
        key = cache.fingerprint("q")
        cache.set(key, [{"id": 1}])

        clock.advance(29)
        assert cache.get(key) == [{"id": 1}]

        clock.advance(2)  # تجاوز 30 ثانية
        assert cache.get(key) is None
        assert cache.stats()["expirations"] == 1

    def test_lru_eviction(self):
        cache = QueryCache(ttl_seconds=60, max_entries=2, clock=FakeClock())
        k1, k2, k3 = (cache.fingerprint(f"q{i}") for i in range(3))
        cache.set(k1, [{"id": 1}])
        cache.set(k2, [{"id": 2}])
        cache.set(k3, [{"id": 3}])  # يجب إخلاء الأقدم (k1)

        assert len(cache) == 2
        assert cache.get(k1) is None
        assert cache.get(k2) == [{"id": 2}]
        assert cache.get(k3) == [{"id": 3}]

    def test_recent_access_protects_from_eviction(self):
        cache = QueryCache(ttl_seconds=60, max_entries=2, clock=FakeClock())
        k1, k2, k3 = (cache.fingerprint(f"q{i}") for i in range(3))
        cache.set(k1, [{"id": 1}])
        cache.set(k2, [{"id": 2}])
        cache.get(k1)               # k1 صار الأحدث استخداماً
        cache.set(k3, [{"id": 3}])  # يجب إخلاء k2

        assert cache.get(k1) is not None
        assert cache.get(k2) is None
        assert cache.stats()["lru_evictions"] == 1

    def test_invalidate_clears_and_counts(self, cache):
        key = cache.fingerprint("q")
        cache.set(key, [{"id": 1}])
        assert cache.invalidate() == 1
        assert len(cache) == 0
        assert cache.get(key) is None
        assert cache.stats()["invalidations"] == 1

    def test_disabled_when_ttl_is_zero(self):
        cache = QueryCache(ttl_seconds=0, max_entries=10, clock=FakeClock())
        key = cache.fingerprint("q")
        cache.set(key, [{"id": 1}])
        assert cache.enabled is False
        assert cache.get(key) is None
        assert len(cache) == 0

    def test_values_are_isolated_copies(self, cache):
        key = cache.fingerprint("q")
        original = [{"id": 1, "tags": ["a"]}]
        cache.set(key, original)

        original[0]["id"] = 999              # تعديل المصدر لا يؤثر على المخزأ
        fetched = cache.get(key)
        assert fetched[0]["id"] == 1

        fetched[0]["tags"].append("b")       # تعديل المسترجَع لا يؤثر على المخزأ
        assert cache.get(key)[0]["tags"] == ["a"]

    def test_hit_rate_and_size(self, cache):
        key = cache.fingerprint("q")
        cache.set(key, [])
        cache.get(key)
        cache.get(key)
        cache.get(cache.fingerprint("other"))
        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["hit_rate"] == pytest.approx(2 / 3, abs=1e-3)

    def test_thread_safety_smoke(self, cache):
        """قراءات/كتابات متوازية لا تُفسد البنية."""
        key = cache.fingerprint("q")
        cache.set(key, [{"id": 1}])
        errors = []

        def worker():
            try:
                for _ in range(200):
                    cache.set(key, [{"id": 1}])
                    assert cache.get(key) is not None
            except Exception as exc:  # pragma: no cover - يظهر فقط عند فشل التزامن
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []


class TestDatabaseCacheIntegration:
    """دمج الطبقة مع SovereignRAGDatabase: إصابة/إبطال/تجاوز."""

    @pytest.fixture
    def rag_db(self, temp_dir):
        db = SovereignRAGDatabase(db_path=temp_dir / "cache_test.db")
        db.upsert_document(
            path="test/doc1.html",
            title="خدمات التحكيم",
            category="web_portal",
            file_hash="hash1",
            chunks=[
                {"title": "التحكيم التجاري", "content": "التحكيم التجاري الدولي لقضايا DIFC و SIAC"},
                {"title": "الضمان الذكي", "content": "الضمان الذكي والضمانات المالية للعقود"},
            ],
        )
        yield db
        reset_query_caches()

    def test_first_query_misses_then_hits(self, rag_db):
        results, meta = rag_db.search_with_cache("التحكيم التجاري", top_k=2)
        assert meta["status"] == "miss"
        assert results

        again, meta2 = rag_db.search_with_cache("التحكيم التجاري", top_k=2)
        assert meta2["status"] == "hit"
        assert again == results

    def test_cached_matches_uncached_results(self, rag_db):
        cached = rag_db.hybrid_search_cached("الضمان الذكي", top_k=2)
        direct = rag_db.hybrid_search("الضمان الذكي", top_k=2)
        assert cached == direct

    def test_bypass_skips_cache(self, rag_db):
        _results, meta = rag_db.search_with_cache("التحكيم", use_cache=False)
        assert meta["status"] == "bypass"
        assert meta["reason"] == "by_request"

    def test_write_invalidates_cache(self, rag_db):
        rag_db.search_with_cache("التحكيم التجاري")
        assert rag_db.search_with_cache("التحكيم التجاري")[1]["status"] == "hit"

        rag_db.upsert_document(
            path="test/doc2.html",
            title="مستند جديد",
            category="documentation",
            file_hash="hash2",
            chunks=[{"title": "جديد", "content": "محضر جلسة تحكيم جديد مع أدلة إضافية"}],
        )
        _results, meta = rag_db.search_with_cache("التحكيم التجاري")
        assert meta["status"] == "miss"

    def test_clear_cache(self, rag_db):
        rag_db.search_with_cache("التحكيم التجاري")
        assert rag_db.clear_cache() == 1
        assert rag_db.search_with_cache("التحكيم التجاري")[1]["status"] == "miss"

    def test_cache_stats_payload(self, rag_db):
        rag_db.search_with_cache("التحكيم التجاري")
        stats = rag_db.cache_stats()
        for key in ("enabled", "ttl_seconds", "max_entries", "size", "hits", "misses", "hit_rate"):
            assert key in stats
        assert stats["db_path"].endswith("cache_test.db")
        assert "\\" not in stats["namespace"] and "/" not in stats["namespace"]

    def test_get_stats_includes_cache_block(self, rag_db):
        stats = rag_db.get_stats()
        assert "query_cache" in stats
        assert stats["query_cache"]["enabled"] is True

    def test_disabled_cache_never_hits(self, temp_dir):
        db = SovereignRAGDatabase(db_path=temp_dir / "nocache.db")
        db._cache = QueryCache(ttl_seconds=0, max_entries=0, clock=FakeClock())
        db.upsert_document(
            path="d.html", title="t", category="c", file_hash="h",
            chunks=[{"title": "t", "content": "نص للاختبار"}],
        )
        _r1, meta1 = db.search_with_cache("نص")
        _r2, meta2 = db.search_with_cache("نص")
        assert meta1["status"] == "bypass"
        assert meta2["status"] == "bypass"
        assert meta2["reason"] == "cache_disabled"
