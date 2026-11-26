"""
==============================================================================
S&R CoreSync For Intelligent Solutions - Sovereign Platform
PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY

Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
Unauthorized copying, decompilation, redistribution, or external model training
of this file, via any medium, is strictly prohibited.
==============================================================================
"""

import os
import sys
import re
import json
import math
import time
import struct
import sqlite3
import hashlib
import logging
import threading
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Dict, Any, Tuple, Optional

# ضبط الترميز لدعم العربية في الطرفية
sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("sr_rag_engine")

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "sr_rag_knowledge.db"
VECTOR_DIM = 128

# إعدادات التخزين المؤقت للاستعلامات (يمكن ضبطها من البيئة)
DEFAULT_CACHE_TTL_SECONDS = 300.0      # عمر القطعة المخزأة: 5 دقائق
DEFAULT_CACHE_MAX_ENTRIES = 256        # سقف عدد الاستعلامات المخزأة (LRU)
MAX_CHUNKS_PER_DOC = 2                 # تنويع النتائج: لا تحتكر صفحة واحدة قائمة النتائج

# يُرفع عند تغيير التطبيع/الاشتقاق/المخطط → الفهرس كله مشتق، فيُعاد بناؤه
INDEX_VERSION = 2


def _env_float(name: str, default: float) -> float:
    try:
        value = os.getenv(name, "")
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        value = os.getenv(name, "")
        return int(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default

# ==============================================================================
# 1. تطبيع النصوص واستخراج المتجهات الكثيفة محلياً (Dense Vector Embedder)
# ==============================================================================

def normalize_text(text: str) -> str:
    """تطبيع النصوص العربية والإنجليزية لإزالة التشكيل وتوحيد الحروف."""
    if not text:
        return ""
    # تطبيع الحروف العربية
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)  # إزالة التشكيل
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    # تنظيف المسافات والرموز الزائدة
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip().lower()


# ==============================================================================
# 1.a كلمات الوقف والاشتقاق الخفيف (Stopwords + Arabic Light Stemming)
# ==============================================================================
# لماذا: الاستعلام «ما هي باقاتكم؟» كان يطابق كل الصفحات لأن «ما» و«هي» تظهران في
# كل نص (BM25 ≈ 0.83 للجميع)، وكانت «باقاتكم» لا تطابق «باقات» أصلاً. النتيجة:
# ترتيب شبه عشوائي. الحلّ: إسقاط الوقف ثم اشتقاق خفيف متسق على طرفي الفهرسة
# والاستعلام، بحيث يصبح «باقاتكم» = «باقات» = «الباقات».
_RAW_ARABIC_STOPWORDS = """
ما هي هو هم هن انا انت انتم نحن من في على عن الي ان او اي ايضا هل ثم قد لقد
كان كانت يكون تكون هذا هذه ذلك تلك هولاء الذي التي الذين اللذان كل بعض غير
بين بعد قبل عند مع يا اما لكن كما حيث حتى اذا كيف متي كم اين لماذا ماذا هناك هنا
الان جدا فقط عليه عليها به بها له لها و ف ب ل ك
""".split()

ARABIC_STOPWORDS = frozenset(
    normalize_text(word) for word in _RAW_ARABIC_STOPWORDS if normalize_text(word)
)

ENGLISH_STOPWORDS = frozenset("""
the a an and or of to in on for with what is are was were be been being do does did
your you we our it its this that these those how why when where which who whom from
at by as about into over under can could should would will just not no yes
""".split())

_AR_PREFIXES = (("وال", 3), ("بال", 3), ("كال", 3), ("فال", 3), ("لل", 3), ("ال", 3), ("و", 4))
# (اللاحقة، أقل طول يجب أن يبقى بعده)
# ملاحظة مقصودة: لا نقلّم «ات» ولا «ه» حتى لا ينفصل «باقات» عن «باقة» ثم
# ينكسر التطابق بين «باقات» و«الباقات» و«وباقات» — السابقة «ال/و» تكفي لتوحيدها.
_AR_SUFFIXES = (
    ("كما", 3), ("هما", 3), ("كم", 3), ("كن", 3), ("هم", 3), ("هن", 3),
    ("ها", 3), ("نا", 3), ("ون", 4), ("ين", 4), ("يه", 4), ("ي", 3),
)

_TOKEN_RE = re.compile(r"[0-9a-z\u0600-\u06FF]+")
# علامات ترقيم عربية تقع داخل نطاق الحروف (؟ ، ؛ ٪ …) فتُستبدل بمسافة قبل التقطيع
_AR_PUNCT_TABLE = str.maketrans({
    ch: " " for ch in "\u060c\u061b\u061f\u066a\u066b\u066c\u06d4\u0640"
})


def light_stem(word: str) -> str:
    """اشتقاق عربي خفيف: يوحّد السوابق واللواحق الشائعة بلا قوائم جذور."""
    stem = word or ""
    if len(stem) < 3:
        return stem
    for prefix, min_rest in _AR_PREFIXES:
        if stem.startswith(prefix) and len(stem) - len(prefix) >= min_rest:
            stem = stem[len(prefix):]
            break
    for suffix, min_rest in _AR_SUFFIXES:
        if stem.endswith(suffix) and len(stem) - len(suffix) >= min_rest:
            stem = stem[:-len(suffix)]
            break
    return stem


def stem_tokens(text: str, drop_stopwords: bool = True) -> List[str]:
    """كلمات النص بعد التطبيع وإسقاط الوقف والاشتقاق، مع الحفاظ على التكرار (BM25)."""
    tokens: List[str] = []
    cleaned = normalize_text(text).translate(_AR_PUNCT_TABLE)
    for token in _TOKEN_RE.findall(cleaned):
        if len(token) < 2:
            continue
        if drop_stopwords and (token in ARABIC_STOPWORDS or token in ENGLISH_STOPWORDS):
            continue
        stem = light_stem(token)
        if len(stem) >= 2:
            tokens.append(stem)
    return tokens


def stem_text(text: str) -> str:
    """نص مشتق يُخزَّن في عمود FTS مستقل ليطابق الاستعلام المشتق."""
    return " ".join(stem_tokens(text))


def query_terms(text: str) -> List[str]:
    """مصطلحات الاستعلام الفريدة بالترتيب (بلا وقف، مشتقة)."""
    terms: List[str] = []
    for token in stem_tokens(text):
        if token not in terms:
            terms.append(token)
    return terms


# ==============================================================================
# 1.b خريطة الترسيخ (Query Pinning) — بيانات خارجية قابلة للتحرير
# ==============================================================================
# لماذا: سؤال «ما هي باقاتكم؟» لا يجد صفحة الباقات لأنها تسمّي خططها Core
# Starter / Business Pro ولا تكرار لكلمة «باقات» في متنها. جُرّبت توسيعات
# معجمية وعقوبات ملاحية فانحدرت الترتيب، فالحلّ المحسوم هو ترسيخ صريح
# (data-driven) لعدد صغير من الأسئلة المعروفة، يُطبّق قبل الترتيب المعجمي
# ولا يُغيّر سلوك أي استعلام لا يطابق محفّزاته.
PINS_PATH = PROJECT_ROOT / "rag_pins.json"
_PINS_CACHE: Dict[str, Any] = {"key": None, "pins": []}


def load_pins(path=None) -> List[Dict[str, Any]]:
    """
    تحميل خريطة الترسيخ مع تخزين مؤقت بحسب بصمة الملف.
    ملف غائب أو تالف → لا ترسيخ (فشل آمن، لا استثناء).
    """
    file_path = Path(path or PINS_PATH)
    try:
        mtime = file_path.stat().st_mtime_ns
    except OSError:
        return []
    cache_key = (str(file_path.resolve()), mtime)
    if _PINS_CACHE["key"] == cache_key:
        return _PINS_CACHE["pins"]

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("تعذر تحميل خريطة الترسيخ %s: %s", file_path, exc)
        return []

    pins: List[Dict[str, Any]] = []
    for raw in data.get("pins", []):
        triggers = frozenset(
            token for term in raw.get("terms", []) for token in stem_tokens(str(term))
        )
        anchors = frozenset(
            token for term in raw.get("chunk_terms", []) for token in stem_tokens(str(term))
        )
        path_value = str(raw.get("path", "")).strip()
        if not triggers or not path_value:
            continue
        pins.append({
            "name": str(raw.get("name") or path_value),
            "triggers": triggers,
            "anchors": anchors,
            "path": path_value,
            "require": max(1, int(raw.get("require", 1))),
            "priority": int(raw.get("priority", 0)),
            "score": min(1.0, max(0.0, float(raw.get("score", 0.92)))),
            "max_chunks": max(1, int(raw.get("max_chunks", 2))),
        })

    _PINS_CACHE["key"] = cache_key
    _PINS_CACHE["pins"] = pins
    if pins:
        logger.info("تم تحميل %d قاعدة ترسيخ من %s", len(pins), file_path)
    return pins


def reset_pins_cache() -> None:
    _PINS_CACHE["key"] = None
    _PINS_CACHE["pins"] = []


def match_pin(terms: List[str], pins: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    أفضل قاعدة ترسيخ تنطبق على مصطلحات الاستعلام.
    الأولوية: عدد المحفّزات المطابقة ثم priority (لأخذ الأكثر تحديداً عند التعادل).
    """
    if not terms:
        return None
    best = None
    best_key = None
    for pin in (pins if pins is not None else load_pins()):
        matched = sum(1 for term in terms if term in pin["triggers"])
        if matched < pin["require"]:
            continue
        # priority أولاً: خريطة صريحة ومُدارة، فصاحب الأولوية الأعلى يحسم التعادل
        key = (pin["priority"], matched)
        if best_key is None or key > best_key:
            best, best_key = pin, key
    return best


def compute_dense_vector(text: str, dim: int = VECTOR_DIM) -> List[float]:
    """
    توليد متجهة كثيفة (Dense Vector) بطول 128 بُعداً معيارياً (L2 Normalized)
    مستندة إلى مزيج من الكلمات والـ Character 3-grams والـ 4-grams
    لتمثيل المعنى السياقي والمورفولوجي العربي واللاتيني بكفاءة فائقة وسرعة دون اعتماديات خارجية.
    """
    clean = normalize_text(text)
    if not clean:
        return [0.0] * dim

    vec = [0.0] * dim
    words = clean.split()

    # 1. تضمين الكلمات
    for w in words:
        if len(w) < 2:
            continue
        h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
        vec[idx] += 1.5 * sign

    # 2. تضمين الـ n-grams للتشابه الصرفي (Subword morphology)
    for i in range(len(clean) - 2):
        trigram = clean[i:i+3]
        h = int(hashlib.md5(trigram.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
        vec[idx] += 0.8 * sign

    for i in range(len(clean) - 3):
        fourgram = clean[i:i+4]
        h = int(hashlib.md5(fourgram.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
        vec[idx] += 0.6 * sign

    # تطبيع المتجهة بالمعيار الإقليدي L2 Norm
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-9:
        vec = [x / norm for x in vec]
    else:
        vec = [0.0] * dim

    return vec

def vector_to_blob(vec: List[float]) -> bytes:
    """تحويل المتجهة إلى تمثيل ثنائي مدمج BLOB."""
    return struct.pack(f"{len(vec)}f", *vec)

def blob_to_vector(blob: bytes) -> List[float]:
    """استرجاع المتجهة من الـ BLOB."""
    count = len(blob) // 4
    return list(struct.unpack(f"{count}f", blob))

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """حساب التشابه الجيبي (Cosine Similarity) بين متجهتين معياريتين."""
    if len(v1) != len(v2) or not v1 or not v2:
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))

# ==============================================================================
# 1.b طبقة التخزين المؤقت لاستعلامات RAG (Query Cache: Fingerprint + TTL + LRU)
# ==============================================================================

class QueryCache:
    """
    ذاكرة مؤقتة لنتائج البحث الهجين.

    لماذا: البحث الهجين يقرأ كل القطع من SQLite ويحسب تشابه المتجهات لكل قطعة في
    كل استدعاء. الأسئلة المتكررة (نفس الاستفسار/الواجهة/جلسة المحاكاة) تُعاد
    من الذاكرة فتوفّر القراءة والحساب وتسرّع الاستجابة. المفتاح = بصمة SHA-256
    (الاستعلام المُطبَّع + top_k + alpha + إصدار الفهرس)، فلا يختلط استعلام بآخر
    ولا تُخدم نتيجة قديمة بعد كتابة جديدة.

    الأمان: النسخ عند القراءة والكتابة (deepcopy) حتى لا يُفسد مستدعٍ النتائج
    المخزأة للآخرين. الحماية: threading.RLock لأن FastAPI قد يخدم طلبات متزامنة.

    TTL = 0 أو أقل يعطّل الطبقة بالكامل (سلوك ما قبل الإضافة).
    """

    def __init__(self, ttl_seconds: Optional[float] = None,
                 max_entries: Optional[int] = None,
                 namespace: str = "default",
                 clock: Callable[[], float] = time.monotonic):
        self.ttl_seconds = (
            float(ttl_seconds) if ttl_seconds is not None
            else _env_float("CORESYNC_RAG_CACHE_TTL", DEFAULT_CACHE_TTL_SECONDS)
        )
        self.max_entries = (
            int(max_entries) if max_entries is not None
            else _env_int("CORESYNC_RAG_CACHE_MAX_ENTRIES", DEFAULT_CACHE_MAX_ENTRIES)
        )
        self.namespace = namespace
        self._clock = clock
        self._lock = threading.RLock()
        self._entries: "OrderedDict[str, Tuple[List[Dict[str, Any]], float]]" = OrderedDict()
        self._version = 0
        self._hits = 0
        self._misses = 0
        self._stores = 0
        self._expirations = 0
        self._lru_evictions = 0
        self._invalidations = 0
        self._last_invalidated_at: Optional[str] = None

    # --- الحالة ----------------------------------------------------------------
    @property
    def enabled(self) -> bool:
        return self.ttl_seconds > 0 and self.max_entries > 0

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    # --- المفتاح ----------------------------------------------------------------
    def fingerprint(self, query: str, top_k: int = 4, alpha: float = 0.55) -> str:
        """بصمة مستقرة للاستعلام: تطبيع عربي/لاتيني + معاملات البحث + إصدار الفهرس."""
        payload = "|".join((
            self.namespace,
            str(self._version),
            normalize_text(query or ""),
            str(int(top_k)),
            f"{float(alpha):.4f}",
        ))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # --- القراءة والكتابة -------------------------------------------------------
    def get(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """نتيجة مخزأة صالحة (نسخة مستقلة) أو None مع احتساب miss."""
        if not self.enabled:
            return None
        with self._lock:
            item = self._entries.get(key)
            if item is None:
                self._misses += 1
                return None
            value, expires_at = item
            if expires_at <= self._clock():
                del self._entries[key]
                self._expirations += 1
                self._misses += 1
                return None
            self._entries.move_to_end(key)  # LRU: الأحدث استخداماً في النهاية
            self._hits += 1
            return deepcopy(value)

    def set(self, key: str, value: List[Dict[str, Any]]) -> None:
        """تخزين نتيجة مع طابع انتهاء، مع إخلاء الأقدم عند تجاوز السقف."""
        if not self.enabled:
            return
        with self._lock:
            self._entries[key] = (deepcopy(value), self._clock() + self.ttl_seconds)
            self._entries.move_to_end(key)
            self._stores += 1
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
                self._lru_evictions += 1

    def invalidate(self) -> int:
        """إبطال كل النتائج (بعد أي كتابة في الفهرس) وإرجاع عدد المُزال."""
        with self._lock:
            removed = len(self._entries)
            self._entries.clear()
            self._version += 1
            self._invalidations += 1
            self._last_invalidated_at = datetime.now().isoformat()
            return removed

    # --- الإحصاءات --------------------------------------------------------------
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            lookups = self._hits + self._misses
            return {
                "enabled": self.enabled,
                "namespace": self.namespace,
                "ttl_seconds": self.ttl_seconds,
                "max_entries": self.max_entries,
                "size": len(self._entries),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / lookups, 4) if lookups else 0.0,
                "stores": self._stores,
                "expirations": self._expirations,
                "lru_evictions": self._lru_evictions,
                "invalidations": self._invalidations,
                "last_invalidated_at": self._last_invalidated_at,
            }


# سجل عمليات: ذاكرة واحدة لكل مسار قاعدة بيانات، حتى تتشاركها كل الكائنات
_CACHE_REGISTRY: Dict[str, QueryCache] = {}
_CACHE_REGISTRY_LOCK = threading.Lock()


def get_shared_query_cache(db_path) -> QueryCache:
    """إرجاع الذاكرة المؤقتة المشتركة لقاعدة بيانات معينة (إنشاء عند أول طلب)."""
    key = str(Path(db_path).resolve())
    with _CACHE_REGISTRY_LOCK:
        cache = _CACHE_REGISTRY.get(key)
        if cache is None:
            cache = QueryCache(namespace=key)
            _CACHE_REGISTRY[key] = cache
        return cache


def reset_query_caches() -> None:
    """إفراغ سجل الذاكرات (للاختبارات أو بعد تغيير إعدادات البيئة)."""
    with _CACHE_REGISTRY_LOCK:
        for cache in _CACHE_REGISTRY.values():
            cache.invalidate()
        _CACHE_REGISTRY.clear()


# ==============================================================================
# 2. مستودع المعرفة الهجين (SQLite Hybrid Store + FTS5)
# ==============================================================================

class SovereignRAGDatabase:
    def __init__(self, db_path: Path = DB_PATH, cache: Optional[QueryCache] = None,
                 cache_ttl: Optional[float] = None):
        self.db_path = str(db_path)
        self._cache = cache if cache is not None else get_shared_query_cache(self.db_path)
        if cache_ttl is not None:
            self._cache.ttl_seconds = float(cache_ttl)
        self._init_schema()

    def get_connection(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA journal_mode = WAL;")
        con.execute("PRAGMA synchronous = NORMAL;")
        return con

    def _init_schema(self):
        with self.get_connection() as con:
            con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);")
            row = con.execute("SELECT value FROM meta WHERE key = 'index_version'").fetchone()
            stored_version = row[0] if row else None
            if stored_version != str(INDEX_VERSION):
                # الفهرس كله مشتق من الملفات: نُسقطه ونعيد بناءه عند تغيّر التطبيع/المخطط
                con.executescript("""
                DROP TABLE IF EXISTS chunks_fts;
                DROP TABLE IF EXISTS chunks;
                DROP TABLE IF EXISTS documents;
                """)
            con.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                title TEXT,
                category TEXT,
                file_hash TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                content_stem TEXT NOT NULL DEFAULT '',
                vector_blob BLOB NOT NULL,
                FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            -- عمود content_stem: صيغة مشتقة من المحتوى ليطابقها الاستعلام المشتق
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                title,
                content,
                content_stem,
                content='chunks',
                content_rowid='id'
            );

            -- Triggers to sync FTS5 with chunks table
            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, title, content, content_stem)
                VALUES (new.id, new.title, new.content, new.content_stem);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, title, content, content_stem)
                VALUES('delete', old.id, old.title, old.content, old.content_stem);
            END;

            CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, title, content, content_stem)
                VALUES('delete', old.id, old.title, old.content, old.content_stem);
                INSERT INTO chunks_fts(rowid, title, content, content_stem)
                VALUES (new.id, new.title, new.content, new.content_stem);
            END;
            """)
            con.execute(
                "INSERT OR REPLACE INTO meta(key, value) VALUES('index_version', ?)",
                (str(INDEX_VERSION),),
            )

    def get_document_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT id, path, title, category, file_hash, updated_at FROM documents WHERE path = ?", (path,))
            row = cur.fetchone()
            if row:
                return {
                    "id": row[0], "path": row[1], "title": row[2],
                    "category": row[3], "file_hash": row[4], "updated_at": row[5]
                }
            return None

    def upsert_document(self, path: str, title: str, category: str, file_hash: str, chunks: List[Dict[str, Any]]):
        with self.get_connection() as con:
            cur = con.cursor()
            now = datetime.now().isoformat()
            
            # Check existing document
            cur.execute("SELECT id FROM documents WHERE path = ?", (path,))
            existing = cur.fetchone()
            
            if existing:
                doc_id = existing[0]
                cur.execute(
                    "UPDATE documents SET title = ?, category = ?, file_hash = ?, updated_at = ? WHERE id = ?",
                    (title, category, file_hash, now, doc_id)
                )
                # Delete old chunks
                cur.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            else:
                cur.execute(
                    "INSERT INTO documents (path, title, category, file_hash, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (path, title, category, file_hash, now)
                )
                doc_id = cur.lastrowid

            # Insert new chunks with vector BLOBs
            for idx, ch in enumerate(chunks):
                vec = compute_dense_vector(f"{ch.get('title', '')} {ch['content']}")
                blob = vector_to_blob(vec)
                cur.execute(
                    "INSERT INTO chunks (doc_id, chunk_index, title, content, content_stem, vector_blob) VALUES (?, ?, ?, ?, ?, ?)",
                    (doc_id, idx, ch.get("title", title), ch["content"], stem_text(ch["content"]), blob)
                )

        # أي كتابة في الفهرس تُبطل النتائج المخزأة: لا نخدم سياقاً قديماً أبداً
        self._cache.invalidate()

    def hybrid_search(self, query: str, top_k: int = 4, alpha: float = 0.25) -> List[Dict[str, Any]]:
        """
        البحث الهجين: تغطية مصطلحات الاستعلام (بعد الاشتقاق) + BM25 (FTS5) + متجهات كثيفة.

        alpha: وزن القناة الكثيفة (0.25 افتراضياً). داخل القناة المعجمية:
            0.72 × تغطية المصطلحات + 0.28 × BM25، والتغطية تُضخَّم حتى 30% عند
            ظهور المصطلح في العنوان (أقوى دلالة من ظهوره في نص عابر).
        التغطية تُرجَّح على التطابق الجزئي: استعلام بثلاثة مصطلحات يتقدّم فيه من
        يطابقها كلها على من يطابق واحداً، وهذا ما كان مفقوداً سابقاً.
        """
        terms = query_terms(query)
        if not terms:
            # استعلام من كلمات وقف فقط («ما هي؟») لا يحمل دلالة بحث
            return []

        query_vec = compute_dense_vector(query)
        total_terms = len(terms)

        with self.get_connection() as con:
            cur = con.cursor()

            # 1. FTS5/BM25 على النص المشتق
            fts_scores: Dict[int, float] = {}
            fts_query = " OR ".join(f'"{t}"*' for t in terms)
            try:
                cur.execute("""
                    SELECT rowid, rank
                    FROM chunks_fts
                    WHERE chunks_fts MATCH ?
                    ORDER BY rank
                    LIMIT 80
                """, (fts_query,))
                rows = cur.fetchall()
            except Exception:
                rows = []
            if rows:
                raws = [abs(r[1]) for r in rows]
                best_raw, worst_raw = min(raws), max(raws)
                span = worst_raw - best_raw
                for r_id, rank in rows:
                    raw = abs(rank)
                    # min-max: توزيع [0,1] على مرشحي هذا الاستعلام بدل تشبّع الجميع عند 1.0
                    fts_scores[r_id] = 1.0 if span <= 1e-9 else (worst_raw - raw) / span

            # 2. مسح القطع: تغطية المصطلحات + المتجهات الكثيفة
            cur.execute("""
                SELECT c.id, c.doc_id, c.title, c.content, c.content_stem,
                       c.vector_blob, d.path, d.category
                FROM chunks c
                JOIN documents d ON c.doc_id = d.id
            """)
            all_chunks = cur.fetchall()

            scored_results = []
            for c_id, doc_id, ch_title, ch_content, ch_stem, vec_blob, doc_path, category in all_chunks:
                content_terms = set((ch_stem or "").split())
                if not content_terms:
                    continue

                matched = sum(1 for t in terms if t in content_terms)
                bm25_sim = fts_scores.get(c_id, 0.0)
                if matched == 0 and bm25_sim == 0.0:
                    continue  # لا صلة معجمية إطلاقاً

                coverage = matched / total_terms
                title_terms = set(stem_text(ch_title).split())
                title_coverage = (
                    sum(1 for t in terms if t in title_terms) / total_terms
                )
                lexical = coverage * (1.0 + 0.5 * title_coverage)

                dense_sim = cosine_similarity(query_vec, blob_to_vector(vec_blob))
                combined_score = (
                    alpha * max(0.0, dense_sim)
                    + (1.0 - alpha) * (0.72 * lexical + 0.28 * bm25_sim)
                )

                scored_results.append({
                    "id": c_id,
                    "doc_id": doc_id,
                    "title": ch_title,
                    "content": ch_content,
                    "path": doc_path,
                    "category": category,
                    "coverage": round(coverage, 4),
                    "title_coverage": round(title_coverage, 4),
                    "dense_score": round(dense_sim, 4),
                    "bm25_score": round(bm25_sim, 4),
                    "score": round(min(1.0, combined_score), 4),
                })

            # ترتيب: الدرجة ثم التغطية (فاصل حاسم عند تعادل الدرجات)
            scored_results.sort(key=lambda x: (x["score"], x["coverage"]), reverse=True)

            # ترسيخ صريح لأسئلة معروفة (قبل التنويع): يُضمن المقطع الصحيح حتى لو
            # لم تحتوِ الصفحة لفظ السؤال (باقات ↔ Core Starter / Business Pro)
            pin = match_pin(terms)
            if pin:
                pinned = self._pinned_matches(cur, pin, terms, query_vec)
                if pinned:
                    pinned_ids = {item["id"] for item in pinned}
                    scored_results = pinned + [r for r in scored_results if r["id"] not in pinned_ids]

            # تنويع: لا تحتكر صفحة واحدة (شريط تنقّل مكرر) قائمة النتائج
            selected: List[Dict[str, Any]] = []
            per_doc: Dict[int, int] = {}
            for result in scored_results:
                if len(selected) >= top_k:
                    break
                if per_doc.get(result["doc_id"], 0) >= MAX_CHUNKS_PER_DOC:
                    continue
                selected.append(result)
                per_doc[result["doc_id"]] = per_doc.get(result["doc_id"], 0) + 1

            if len(selected) < top_k:
                for result in scored_results:
                    if len(selected) >= top_k:
                        break
                    if result not in selected:
                        selected.append(result)

            return selected

    def _pinned_matches(self, cur, pin: Dict[str, Any], terms: List[str],
                        query_vec: List[float]) -> List[Dict[str, Any]]:
        """
        مقاطع الوثيقة المثبّتة، مرتّبة بتطابق المراسي ثم تغطية مصطلحات السؤال.
        تتجاوز مرشّح «لا صلة معجمية» عمداً: الصفحة الصحيحة قد لا تذكر لفظ السؤال.
        توثيق غائب أو بلا مراسٍ مطابقة → لا نتائج (فشل آمن، يكمل الترتيب الطبيعي).
        """
        cur.execute("""
            SELECT c.id, c.doc_id, c.title, c.content, c.content_stem,
                   c.vector_blob, d.path, d.category, c.chunk_index
            FROM chunks c JOIN documents d ON c.doc_id = d.id
            WHERE d.path = ?
        """, (pin["path"],))
        rows = cur.fetchall()
        if not rows:
            return []

        anchors = pin["anchors"]
        total_terms = len(terms) or 1
        ranked = []
        for c_id, doc_id, ch_title, ch_content, ch_stem, vec_blob, doc_path, category, chunk_index in rows:
            # المراسي تُطابق العنوان أيضاً: «Core Starter» في العنوان لا في المتن
            tokens = set((ch_stem or "").split()) | set(stem_text(ch_title).split())
            anchor_hits = sum(1 for anchor in anchors if anchor in tokens) if anchors else 0
            if anchors and anchor_hits == 0:
                continue
            coverage = sum(1 for term in terms if term in tokens) / total_terms
            ranked.append((anchor_hits, coverage, -int(chunk_index or 0),
                           (c_id, doc_id, ch_title, ch_content, vec_blob, doc_path, category)))
        if not ranked:
            return []

        # المراسي أولاً، ثم التغطية، ثم ترتيب المقطع في الصفحة (ثبات النتيجة)
        ranked.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        pinned_results: List[Dict[str, Any]] = []
        for _anchor_hits, coverage, _idx, row in ranked[: pin["max_chunks"]]:
            c_id, doc_id, ch_title, ch_content, vec_blob, doc_path, category = row
            title_terms = set(stem_text(ch_title).split())
            pinned_results.append({
                "id": c_id,
                "doc_id": doc_id,
                "title": ch_title,
                "content": ch_content,
                "path": doc_path,
                "category": category,
                "coverage": round(coverage, 4),
                "title_coverage": round(
                    sum(1 for term in terms if term in title_terms) / total_terms, 4
                ),
                "dense_score": round(cosine_similarity(query_vec, blob_to_vector(vec_blob)), 4),
                "bm25_score": 0.0,
                "score": round(pin["score"], 4),
                "pinned": True,
                "pin": pin["name"],
            })
        return pinned_results

    def hybrid_search_cached(self, query: str, top_k: int = 4, alpha: float = 0.25,
                             use_cache: bool = True) -> List[Dict[str, Any]]:
        """البحث الهجين مع ذاكرة مؤقتة (الواجهة الموصى بها لنقاط النهاية)."""
        results, _meta = self.search_with_cache(query, top_k=top_k, alpha=alpha, use_cache=use_cache)
        return results

    def search_with_cache(self, query: str, top_k: int = 4, alpha: float = 0.25,
                          use_cache: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        بحث هجين مع بيانات وصفية عن حالة الذاكرة (hit / miss / bypass).
        يُستخدم في نقطة النهاية لإظهار ما إذا كانت الاستجابة من الذاكرة أم لا.
        """
        if not use_cache or not self._cache.enabled:
            reason = "cache_disabled" if not self._cache.enabled else "by_request"
            results = self.hybrid_search(query, top_k=top_k, alpha=alpha)
            return results, {"status": "bypass", "reason": reason, "ttl_seconds": self._cache.ttl_seconds}

        key = self._cache.fingerprint(query, top_k=top_k, alpha=alpha)
        cached = self._cache.get(key)
        if cached is not None:
            return cached, {
                "status": "hit",
                "fingerprint": key[:12],
                "ttl_seconds": self._cache.ttl_seconds,
            }

        results = self.hybrid_search(query, top_k=top_k, alpha=alpha)
        self._cache.set(key, results)
        return results, {
            "status": "miss",
            "fingerprint": key[:12],
            "ttl_seconds": self._cache.ttl_seconds,
        }

    def cache_stats(self) -> Dict[str, Any]:
        """إحصاءات طبقة التخزين المؤقت (نسبة الإصابة، الحجم، الإبطالات...)"""
        stats = self._cache.stats()
        # لا نكشف المسار المطلق للقرص في استجابات API؛ اسم الملف يكفي للتشخيص
        stats["namespace"] = Path(self.db_path).name
        stats["db_path"] = Path(self.db_path).name
        return stats

    def clear_cache(self) -> int:
        """إبطال كل النتائج المخزأة وإرجاع عدد القطع المُزالة."""
        return self._cache.invalidate()

    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM documents")
            doc_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM chunks")
            chunk_count = cur.fetchone()[0]
            cur.execute("SELECT path, title, updated_at FROM documents ORDER BY updated_at DESC LIMIT 5")
            recent = [{"path": r[0], "title": r[1], "updated_at": r[2]} for r in cur.fetchall()]
            return {
                "total_documents": doc_count,
                "total_chunks": chunk_count,
                "vector_dimension": VECTOR_DIM,
                "hybrid_mode": "Dense Vector (128-d) + SQLite FTS5 (BM25)",
                "query_cache": self._cache.stats(),
                "recent_documents": recent
            }

# ==============================================================================
# 3. مفكك ومحلل صفحات HTML والملفات الذكي (Sovereign Document Crawler)
# ==============================================================================

def clean_html_to_chunks(html_content: str, source_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """استخراج العنوان وفقرات المحتوى النظيفة من ملف HTML وتقسيمها إلى قطع دلالية."""
    # استخراج عنوان الصفحة
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    page_title = title_match.group(1).strip() if title_match else Path(source_path).stem
    page_title = re.sub(r'\|.*', '', page_title).strip()

    # إزالة أكواد السكربت والأنماط
    clean = re.sub(r'<script.*?</script>', ' ', html_content, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style.*?</style>', ' ', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<svg.*?</svg>', ' ', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<!--.*?-->', ' ', clean, flags=re.DOTALL)

    # تفكيك المقاطع حسب العناوين h1, h2, h3, section
    sections = re.split(r'(<h[1-4][^>]*>.*?</h[1-4]>)', clean, flags=re.IGNORECASE)
    
    chunks = []
    current_title = page_title
    current_text = []

    for part in sections:
        header_match = re.search(r'<h[1-4][^>]*>(.*?)</h[1-4]>', part, re.IGNORECASE | re.DOTALL)
        if header_match:
            # إذا كان هناك نص متراكم سابقاً، نحفظه كقطعة
            if current_text:
                block = " ".join(current_text).strip()
                if len(block) > 60:
                    chunks.append({"title": current_title, "content": block})
                current_text = []
            header_text = re.sub(r'<[^>]+>', ' ', header_match.group(1))
            current_title = f"{page_title} - {header_text.strip()}"
        else:
            # تنظيف وسوم HTML واستخراج النص الخام
            raw_text = re.sub(r'<[^>]+>', ' ', part)
            raw_text = re.sub(r'\s+', ' ', raw_text).strip()
            if raw_text:
                current_text.append(raw_text)

    if current_text:
        block = " ".join(current_text).strip()
        if len(block) > 60:
            chunks.append({"title": current_title, "content": block})

    # تقسيم القطع الكبيرة جداً (> 600 كلمة)
    final_chunks = []
    for ch in chunks:
        words = ch["content"].split()
        if len(words) > 350:
            for i in range(0, len(words), 250):
                sub_block = " ".join(words[i:i+300])
                final_chunks.append({
                    "title": ch["title"],
                    "content": sub_block
                })
        else:
            final_chunks.append(ch)

    return page_title, final_chunks

def parse_markdown_to_chunks(md_content: str, source_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """استخراج العنوان والقطع الدلالية من ملفات Markdown."""
    lines = md_content.splitlines()
    doc_title = Path(source_path).name
    chunks = []
    current_heading = doc_title
    current_lines = []

    for line in lines:
        if line.startswith("#"):
            if current_lines:
                block = "\n".join(current_lines).strip()
                if len(block) > 40:
                    chunks.append({"title": current_heading, "content": block})
                current_lines = []
            current_heading = line.lstrip("#").strip()
        else:
            current_lines.append(line)

    if current_lines:
        block = "\n".join(current_lines).strip()
        if len(block) > 40:
            chunks.append({"title": current_heading, "content": block})

    return doc_title, chunks

def build_or_update_knowledge_index(root_dir: Path = PROJECT_ROOT) -> Dict[str, Any]:
    """
    مسح وفهرسة كافة صفحات وبوابات المشروع وملفات المعرفة السيادية وتوليد المتجهات الهجينة.
    """
    db = SovereignRAGDatabase()
    
    # قائمة الملفات المستهدفة
    target_files = []
    
    # 1. صفحات HTML في الجذر
    for p in root_dir.glob("*.html"):
        # استثناء الملفات المؤقتة غير الأساسية إن وجدت
        if not p.name.startswith("temp_"):
            target_files.append((p, "web_portal"))

    # 2. مقالات المدونة ورؤى المنظومة
    insights_dir = root_dir / "insights"
    if insights_dir.exists():
        for p in insights_dir.glob("*.html"):
            target_files.append((p, "blog_insight"))

    # 3. الوثائق والمستندات الأساسية
    docs = ["README.md", "GEMINI.md", "task.md"]
    for d in docs:
        p = root_dir / d
        if p.exists():
            target_files.append((p, "documentation"))

    indexed_count = 0
    skipped_count = 0
    total_chunks = 0

    for file_path, category in target_files:
        try:
            rel_path = str(file_path.relative_to(root_dir)).replace("\\", "/")
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            existing = db.get_document_by_path(rel_path)

            # تجنب إعادة الفهرسة إذا لم يتغير الملف
            if existing and existing.get("file_hash") == file_hash:
                skipped_count += 1
                continue

            if file_path.suffix.lower() == ".html":
                title, chunks = clean_html_to_chunks(content, rel_path)
            else:
                title, chunks = parse_markdown_to_chunks(content, rel_path)

            if chunks:
                db.upsert_document(
                    path=rel_path,
                    title=title,
                    category=category,
                    file_hash=file_hash,
                    chunks=chunks
                )
                indexed_count += 1
                total_chunks += len(chunks)

        except Exception as e:
            print(f"[RAG Indexer] Error processing {file_path.name}: {e}")

    stats = db.get_stats()
    stats["newly_indexed_docs"] = indexed_count
    stats["skipped_unchanged_docs"] = skipped_count
    return stats

# ==============================================================================
# 4. نقطة استعلام موحدة لمساعد الذكاء الاصطناعي (Agent RAG Tool)
# ==============================================================================

def query_rag_knowledge(query: str, top_k: int = 4) -> str:
    """
    استعلام فوري عن معلومات موثقة من صفحات وخدمات ووثائق المشروع عبر RAG الهجين.
    """
    db = SovereignRAGDatabase()
    results = db.hybrid_search_cached(query, top_k=top_k)
    if not results:
        return "لم يتم العثور على مقاطع مطابقة تماماً في ذاكرة المتجهات المحلية للمشروع."

    output = [f"=== نتائج استرجاع المعرفة السيادية (RAG Context) للاستفسار: '{query}' ==="]
    for i, r in enumerate(results, 1):
        output.append(
            f"\n[{i}] العنوان: {r['title']} | المصدر: {r['path']} (درجة التطابق: {r['score']})\n"
            f"المحتوى:\n{r['content'][:400]}..."
        )
    return "\n".join(output)

def index_custom_document(title: str, text_content: str, source_identifier: str, category: str = "uploaded_document") -> Dict[str, Any]:
    """
    فهرسة محتوى مستند مخصص (مثل مرفقات PDF أو DOCX المرفوعة) وتحديث قاعدة بيانات RAG فورياً.
    """
    db = SovereignRAGDatabase()
    
    # تقسيم النص إلى فقرات وقطع دلالية (Chunks)
    paragraphs = [p.strip() for p in text_content.split("\n\n") if len(p.strip()) > 30]
    if not paragraphs:
        paragraphs = [p.strip() for p in text_content.split("\n") if len(p.strip()) > 30]
    if not paragraphs:
        paragraphs = [text_content.strip()]
    
    chunks = []
    current_chunk = []
    current_len = 0
    
    for para in paragraphs:
        current_chunk.append(para)
        current_len += len(para)
        if current_len >= 450:
            block = "\n".join(current_chunk).strip()
            chunks.append({"title": title, "content": block})
            current_chunk = []
            current_len = 0
            
    if current_chunk:
        block = "\n".join(current_chunk).strip()
        if block:
            chunks.append({"title": title, "content": block})
            
    content_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
    db.upsert_document(
        path=source_identifier,
        title=title,
        category=category,
        file_hash=content_hash,
        chunks=chunks
    )
    return {
        "status": "success",
        "title": title,
        "source": source_identifier,
        "chunks_indexed": len(chunks)
    }

if __name__ == "__main__":
    print("=" * 70)
    print("S&R CoreSync - بناء وفهرسة ذاكرة المتجهات المحلية (Local Vector DB / RAG)")
    print("=" * 70)
    stats = build_or_update_knowledge_index()
    print("إحصائيات الفهرسة:", stats)
    print("\n--- تجربة استعلام دلالي (Semantic Query Test) ---")
    test_res = query_rag_knowledge("ما هي تفاصيل خدمة التحكيم التجاري الدولي؟", top_k=2)
    print(test_res)
