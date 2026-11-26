"""
=============================================================================
اختبارات وحدوية لمحرك معرفة راغ (sr_rag_engine.py)
=============================================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import math
from sr_rag_engine import (
    INDEX_VERSION,
    SovereignRAGDatabase,
    VECTOR_DIM,
    blob_to_vector,
    compute_dense_vector,
    cosine_similarity,
    light_stem,
    load_pins,
    match_pin,
    normalize_text,
    query_terms,
    reset_pins_cache,
    reset_query_caches,
    stem_text,
    vector_to_blob,
)


class TestTextNormalization:
    """اختبارات لدالة تطبيع النصوص."""

    def test_remove_arabic_tashkeel(self):
        """يجب إزالة التشكيل العربي."""
        text = "مَرْحَبًا بِكُمْ"
        result = normalize_text(text)
        assert "َ" not in result
        assert "ُ" not in result
        assert "ِ" not in result

    def test_normalize_alef_variants(self):
        """يجب توحيد أشكال الألف (إ، أ، آ، ا)."""
        text = "إكرام أؤمن آمان الإنسان"
        result = normalize_text(text)
        assert "إ" not in result
        assert "أ" not in result
        assert "آ" not in result

    def test_normalize_lowercase(self):
        """يجب تحويل النص إلى أحرف صغيرة."""
        text = "MERHABA"
        result = normalize_text(text)
        assert result == "merhaba"

    def test_normalize_empty_string(self):
        """يجب إرجاع سلسلة فارغة عند إدخال سلسلة فارغة."""
        result = normalize_text("")
        assert result == ""

    def test_normalize_none(self):
        """يجب إرجاع سلسلة فارغة عند إدخال None."""
        result = normalize_text(None)
        assert result == ""


class TestDenseVector:
    """اختبارات لدالة المتجهات الكثيفة."""

    def test_compute_dense_vector_returns_correct_length(self):
        """يجب أن يعيد المتجه بطول VECTOR_DIM."""
        vec = compute_dense_vector("نص تجريبي للاختبار")
        assert len(vec) == VECTOR_DIM

    def test_compute_dense_vector_is_normalized(self):
        """يجب أن يكون المتجه معياريًا (L2 norm = 1)."""
        vec = compute_dense_vector("نص للتطبيع")
        norm = math.sqrt(sum(x * x for x in vec))
        assert abs(norm - 1.0) < 1e-6

    def test_compute_dense_vector_empty_text(self):
        """يجب إعادة متجه أصفار عند إدخال نص فارغ."""
        vec = compute_dense_vector("")
        assert all(x == 0.0 for x in vec)
        assert len(vec) == VECTOR_DIM

    def test_compute_dense_vector_deterministic(self):
        """يجب أن تكون المتجهات محددة (نفس النص → نفس المتجه)."""
        v1 = compute_dense_vector("نفس النص")
        v2 = compute_dense_vector("نفس النص")
        assert v1 == v2

    def test_compute_dense_vector_different_texts(self):
        """يجب أن تختلف المتجهات للنصوص المختلفة."""


class TestCosineSimilarity:
    """اختبارات لحساب التشابه الجيبي."""

    def test_cosine_similarity_identical_vectors(self):
        """يجب أن يكون التشابه 1.0 للمتجهات المتطابقة."""
        v = [1.0, 0.0, 0.0]
        result = cosine_similarity(v, v)
        assert abs(result - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal_vectors(self):
        """يجب أن يكون التشابه 0.0 للمتجهات المتعامدة."""
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        result = cosine_similarity(v1, v2)
        assert abs(result - 0.0) < 1e-6

    def test_cosine_similarity_different_lengths(self):
        """يجب أن يعيد 0.0 للمتجهات بأطوال مختلفة."""
        v1 = [1.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        result = cosine_similarity(v1, v2)
        assert result == 0.0


class TestSovereignRAGDatabase:
    """اختبارات لفئة قاعدة بيانات راغ السيادية."""

    @pytest.fixture
    def rag_db(self, temp_dir):
        """إنشاء قاعدة بيانات راغ مؤقتة للاختبار."""
        db_path = temp_dir / "test_rag.db"
        db = SovereignRAGDatabase(db_path=db_path)
        yield db

    def test_init_schema_creates_tables(self, rag_db):
        """يجب إنشاء الجداول عند تهيئة قاعدة البيانات."""
        import sqlite3
        with sqlite3.connect(str(rag_db.db_path)) as con:
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            assert "documents" in tables
            assert "chunks" in tables
            assert "chunks_fts" in tables

    def test_upsert_and_get_document(self, rag_db):
        """يجب إدراج واسترجاع مستند."""
        chunks = [
            {"title": "مقدمة", "content": "هذا محتوى تجريبي للاختبار"},
            {"title": "الخلاصة", "content": "ملخص محتوى الاختبار"}
        ]
        rag_db.upsert_document(
            path="test/doc1.html",
            title="الوثيقة التجريبية",
            category="test",
            file_hash="abc123",
            chunks=chunks
        )

        doc = rag_db.get_document_by_path("test/doc1.html")
        assert doc is not None
        assert doc["title"] == "الوثيقة التجريبية"
        assert doc["category"] == "test"

    def test_hybrid_search_returns_results(self, rag_db):
        """يجب إرجاع نتائج عند البحث في قاعدة بيانات غير فارغة."""
        chunks = [
            {"title": "خدمة التحكيم", "content": "التحكيم التجاري الدولي لقضايا DIFC و SIAC"},
            {"title": "باقات السوشيال", "content": "باقة السوشيال ميديا 8K بسعر 890 يورو"},
            {"title": "التدقيق الضريبي", "content": "محرك التدقيق الضريبي المتوافق مع IFRS"}
        ]
        rag_db.upsert_document(
            path="test/services.html",
            title="الخدمات",
            category="web_portal",
            file_hash="def456",
            chunks=chunks
        )

        results = rag_db.hybrid_search("التحكيم التجاري", top_k=2)
        assert len(results) > 0
        assert any("التحكيم" in r["content"] for r in results)

    def test_hybrid_search_empty_query(self, rag_db):
        """يجب إرجاع قائمة فارغة لاستعلام فارغ."""
        results = rag_db.hybrid_search("")
        assert results == []

    def test_get_stats(self, rag_db):
        """يجب إرجاع إحصائيات قاعدة البيانات."""
        stats = rag_db.get_stats()
        assert "total_documents" in stats
        assert "total_chunks" in stats
        assert "vector_dimension" in stats
        assert stats["vector_dimension"] == VECTOR_DIM
        v1 = compute_dense_vector("نص أول")
        v2 = compute_dense_vector("نص ثاني مختلف تمامًا")
        assert v1 != v2


class TestVectorBlobConversion:
    """اختبارات لتحويل المتجهات إلى وحدات ثنائية والعكس."""

    def test_vector_to_blob_roundtrip(self):
        """يجب استعادة المتجه نفسه بعد التحويل إلى وحدة ثنائية والعكس (within float32 precision)."""
        original = [0.1, 0.2, -0.3, 0.5] * 32
        blob = vector_to_blob(original)
        restored = blob_to_vector(blob)
        assert len(original) == len(restored)
        for o, r in zip(original, restored):
            assert abs(o - r) < 1e-6

class TestQueryUnderstanding:
    """الوقف والاشتقاق: أساس ترتيب النتائج."""

    def test_possessive_suffix_is_stripped(self):
        assert query_terms("ما هي باقاتكم؟") == ["باقات"]

    def test_stopwords_are_dropped(self):
        assert query_terms("ما هي؟") == []
        assert query_terms("the and of") == []

    def test_definite_article_and_adjective(self):
        assert query_terms("التحكيم التجاري") == ["تحكيم", "تجار"]

    def test_plural_forms_unify(self):
        assert light_stem("الباقات") == light_stem("باقاتكم") == "باقات"

    def test_short_word_is_not_over_stemmed(self):
        # «باقات» يجب أن تبقى كما هي (لو قُلّمت إلى «باق» لفقدنا التطابق)
        assert light_stem("باقات") == "باقات"

    def test_stem_text_keeps_repetition_for_bm25(self):
        assert stem_text("باقات باقات").split() == ["باقات", "باقات"]

    def test_terms_are_unique_and_ordered(self):
        assert query_terms("الخدمات خدماتنا الخدمات") == ["خدمات"]

    def test_index_version_declared(self):
        assert INDEX_VERSION >= 2


class TestRetrievalRelevance:
    """
    الانحدار الحقيقي: سؤال «ما هي باقاتكم؟» كان يعيد صفحة المحاكي لأن كلمتي
    «ما/هي» تطابقان كل نص، و«باقاتكم» لا تطابق «باقات».
    """

    @pytest.fixture
    def db(self, temp_dir):
        database = SovereignRAGDatabase(db_path=temp_dir / "relevance.db")
        # صفحة محاكي: «الباقات» تظهر فقط داخل شريط تنقّل
        database.upsert_document(
            path="predictive-cashflow-risk.html",
            title="محاكي تحليل وتوقع تدفقات السيولة والمخاطر الائتمانية",
            category="web_portal",
            file_hash="h1",
            chunks=[{
                "title": "محاكي تحليل وتوقع تدفقات السيولة",
                "content": "لوحة القيادة المركزية التسويات عبر الحدود الضمان الذكي "
                           "الرئيسية الخدمات الباقات الأسعار تواصل معنا",
            }],
        )
        # صفحة الباقات الحقيقية
        database.upsert_document(
            path="index.html",
            title="الباقات والأسعار",
            category="web_portal",
            file_hash="h2",
            chunks=[{
                "title": "الباقات والأسعار",
                "content": "باقة السوشيال ميديا 8K بسعر 890 يورو، وباقة المنصة الرقمية، "
                           "وباقات التحكيم والامتثال، مع دعم كامل",
            }],
        )
        yield database
        reset_query_caches()

    def test_pricing_question_returns_pricing_page_first(self, db):
        results = db.hybrid_search("ما هي باقاتكم؟", top_k=3)
        assert results
        assert results[0]["path"] == "index.html"
        assert results[0]["coverage"] == 1.0

    def test_full_coverage_beats_partial_match(self, db):
        db.upsert_document(
            path="sovereign-arbitration-hub.html",
            title="التحكيم التجاري الدولي",
            category="web_portal",
            file_hash="h3",
            chunks=[{
                "title": "التحكيم التجاري الدولي",
                "content": "محرك التحكيم التجاري الدولي وتسوية النزاعات الذكية",
            }],
        )
        results = db.hybrid_search("التحكيم التجاري الدولي", top_k=2)
        assert results[0]["path"] == "sovereign-arbitration-hub.html"
        assert results[0]["coverage"] == 1.0
        # الوثيقة التي تطابق مصطلحاً واحداً تبقى موجودة لكن بأقل
        assert all(r["coverage"] <= results[0]["coverage"] for r in results)

    def test_stopword_only_query_returns_nothing(self, db):
        assert db.hybrid_search("ما هي؟") == []

    def test_results_expose_coverage_fields(self, db):
        top = db.hybrid_search("باقات", top_k=1)[0]
        assert "coverage" in top and "title_coverage" in top
        assert top["score"] <= 1.0


class TestQueryPinning:
    """
    الترسيخ الصريح: أسئلة معروفة تُوجَّه لصفحتها الصحيحة بالبيانات لا بالتخمين.
    صفحة الباقات تسمّي خططها Core Starter / Business Pro ولا تكرّر «باقات».
    """

    def test_repo_pins_load(self):
        pins = load_pins()
        assert {p["name"] for p in pins} >= {"pricing", "social-8k", "contact"}
        assert all(p["triggers"] and p["path"] for p in pins)

    def test_pricing_trigger_matches(self):
        pins = load_pins()
        assert match_pin(["باقات"], pins)["name"] == "pricing"
        assert match_pin(["سعر", "باقه"], pins)["name"] == "pricing"

    def test_priority_breaks_the_tie(self):
        pins = load_pins()
        # «سوشيال» و«سعر» معاً: الأولوية الأعلى (social-8k) تحسم
        assert match_pin(["سوشيال", "سعر"], pins)["name"] == "social-8k"

    def test_no_pin_for_unrelated_query(self):
        pins = load_pins()
        assert match_pin(["تحكيم", "تجار"], pins) is None
        assert match_pin([], pins) is None

    def test_missing_or_broken_file_fails_safe(self, tmp_path):
        assert load_pins(str(tmp_path / "absent.json")) == []
        broken = tmp_path / "broken.json"
        broken.write_text("{ this is not json", encoding="utf-8")
        assert load_pins(str(broken)) == []


class TestPinnedRetrieval:
    """تطبيق الترسيخ على قاعدة بيانات فعلية (فشل آمن عند غياب الوثيقة)."""

    @pytest.fixture
    def db(self, temp_dir):
        reset_pins_cache()
        database = SovereignRAGDatabase(db_path=temp_dir / "pins.db")
        database.upsert_document(
            path="index.html",
            title="S&R CoreSync",
            category="web_portal",
            file_hash="p1",
            chunks=[
                {"title": "S&R CoreSync", "content": "الرئيسية الخدمات الأسعار الباقات المتجر تواصل"},
                {"title": "S&R CoreSync - Core Starter", "content": "للشركات الناشئة € 1,192 / شهرياً"},
                {"title": "S&R CoreSync - Business Pro", "content": "للشركات المتوسطة € 2,312 / شهرياً"},
            ],
        )
        database.upsert_document(
            path="social-8k-studio.html",
            title="استوديو الهوية البصرية وحزمة السوشيال ميديا 8K",
            category="web_portal",
            file_hash="p2",
            chunks=[{"title": "استوديو 8K", "content": "حزمة السوشيال ميديا 8K تشمل شورتس وريلز"}],
        )
        database.upsert_document(
            path="sovereign-arbitration-hub.html",
            title="التحكيم التجاري الدولي",
            category="web_portal",
            file_hash="p3",
            chunks=[{"title": "التحكيم التجاري الدولي", "content": "محرك التحكيم التجاري الدولي وتسوية النزاعات"}],
        )
        yield database
        reset_query_caches()

    def test_pricing_question_is_pinned_to_plan_cards(self, db):
        results = db.hybrid_search("ما هي باقاتكم؟", top_k=3)
        assert results[0]["pinned"] is True
        assert results[0]["path"] == "index.html"
        assert "Core Starter" in results[0]["title"]
        assert "1,192" in results[0]["content"]
        # الخطة الثانية مثبّتة أيضاً
        assert "Business Pro" in results[1]["title"]
        assert results[1]["pinned"] is True

    def test_social_question_wins_over_pricing_pin(self, db):
        results = db.hybrid_search("كم سعر باقة السوشيال ميديا؟", top_k=2)
        assert results[0]["pinned"] is True
        assert results[0]["path"] == "social-8k-studio.html"

    def test_unpinned_query_is_unaffected(self, db):
        results = db.hybrid_search("التحكيم التجاري الدولي", top_k=2)
        assert all(not r.get("pinned") for r in results)
        assert results[0]["path"] == "sovereign-arbitration-hub.html"

    def test_missing_pinned_document_falls_back(self, db):
        # قاعدة تشير إلى وثيقة غير موجودة (صفحة أُعيدت تسميتها) → لا نتائج مثبّتة، بلا انفجار
        ghost = {"name": "ghost", "triggers": frozenset({"باقات"}), "anchors": frozenset(),
                 "path": "ghost.html", "require": 1, "priority": 99, "score": 0.9, "max_chunks": 1}
        with db.get_connection() as con:
            assert db._pinned_matches(con.cursor(), ghost, ["باقات"], [0.0] * VECTOR_DIM) == []

        # والبحث الطبيعي يعمل كما هو
        assert db.hybrid_search("التحكيم التجاري الدولي", top_k=1)

    def test_pin_without_matching_anchor_is_ignored(self, db):
        empty_anchor = {"name": "no-anchor", "triggers": frozenset({"باقات"}),
                        "anchors": frozenset({"xyzzy"}), "path": "index.html",
                        "require": 1, "priority": 99, "score": 0.9, "max_chunks": 1}
        with db.get_connection() as con:
            assert db._pinned_matches(con.cursor(), empty_anchor, ["باقات"], [0.0] * VECTOR_DIM) == []
