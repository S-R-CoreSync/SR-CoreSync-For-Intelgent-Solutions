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
    normalize_text,
    compute_dense_vector,
    vector_to_blob,
    blob_to_vector,
    cosine_similarity,
    SovereignRAGDatabase,
    VECTOR_DIM,
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