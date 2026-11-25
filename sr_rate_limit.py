"""
==============================================================================
S&R CoreSync For Intelligent Solutions - Sovereign Platform
PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY

Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
Unauthorized copying, decompilation, redistribution, or external model training
of this file, via any medium, is strictly prohibited.
==============================================================================

==============================================================================
حدّ معدل الطلبات المشترك بين العمليات (Shared Sliding-Window Rate Limiter)
==============================================================================
المشكلة التي يحلها هذا الملف:
  وسيلة الحدّ في `sr_auth.py` كانت تحتفظ بعدّاداتها في ذاكرة العملية الواحدة.
  عند تشغيل أكثر من عامل (uvicorn --workers N أو gunicorn)، يصبح الحدّ الفعلي
  = الحد × عدد العمال، ويعيد كل عامل تشغيل نافذته الخاصة عند إعادة التشغيل.

الحلّ (بلا أي خدمة مدفوعة أو خارجية):
  - `SQLiteRateLimitStore`: نافذة منزلقة دقيقة في ملف SQLite واحد (WAL +
    BEGIN IMMEDIATE) يشاركه كل العمال والعمليات على نفس المضيف.
  - `MemoryRateLimitStore`: نفس الخوارزمية في الذاكرة (احتياطي، أو لبيئة
    بلا نظام ملفات قابل للكتابة).
  - `create_rate_limit_store`: يختار الخلفية من البيئة مع تدرّج آمن.

الخوارزمية (نافذة منزلقة حقيقية، لا نافذة ثابتة):
  لكل (bucket, identity) نحتفظ بأزمنة الطلبات المقبولة؛ الطلب يُرفض إذا كان
  عدد الطلبات ضمن آخر `window` ثانية قد بلغ `limit`، ويُعاد `retry_after`
  بالثواني حتى يتحرر أقدم طلب. النافذة الثابتة كانت ستسمح بانفجار مضاعف
  (limit في نهاية النافذة + limit في بدايتها) — وهذا مرفوض لحماية حصة النموذج.

سياسة الفشل: **الانفتاح مع تسجيل** (Fail-Open). حدّ المعدل حماية إساءة استخدام
لا وسيلة مصادقة؛ انقطاع القرص لا يجوز أن يُسقط الخدمة كلها. تُسجَّل الحادثة
بمستوى warning لتُراقب.

المتغيرات البيئية:
  CORESYNC_RATE_LIMIT_STORE   auto | sqlite | memory   (افتراضي: auto)
  CORESYNC_RATE_LIMIT_DB      مسار ملف العدّادات       (افتراضي: sr_rate_limit.db)
  CORESYNC_RATE_LIMIT         الحد العام               (يُقرأ في sr_auth: 120/min)
  CORESYNC_CHAT_RATE_LIMIT    حد مسارات المحادثة       (يُقرأ في sr_auth: 10/min)
"""

import os
import sys
import math
import time
import sqlite3
import logging
import threading
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Callable, Deque, Dict, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("sr_rate_limit")

PROJECT_DIR = Path(__file__).resolve().parent

BACKEND_AUTO = "auto"
BACKEND_SQLITE = "sqlite"
BACKEND_MEMORY = "memory"
VALID_BACKENDS = {BACKEND_AUTO, BACKEND_SQLITE, BACKEND_MEMORY}

# أفق تنظيف الصفوف القديمة: أكبر نافذة مدعومة (ساعة) × 2
_CLEANUP_HORIZON_SECONDS = 7200


class RateLimitStore:
    """واجهة مشتركة لمخزن حدّ المعدل."""

    backend: str = "abstract"

    def hit(self, bucket: str, identity: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        تسجيل محاولة واحدة وإرجاع (مسموح؟، ثواني الانتظار المقترحة).
        عند الرفض: retry_after >= 1.
        """
        raise NotImplementedError

    def stats(self) -> Dict[str, Any]:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError


# ==============================================================================
# 1. الخلفية في الذاكرة (احتياطي / اختبارات)
# ==============================================================================
class MemoryRateLimitStore(RateLimitStore):
    """
    نافذة منزلقة في الذاكرة لكل عملية. لا تشارك الحالة مع العمال الآخرين،
    لذا تُستخدم احتياطاً أو في التطوير فقط.
    """

    backend = BACKEND_MEMORY

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._hits: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
        self._rejected = 0
        self._accepted = 0

    def hit(self, bucket: str, identity: str, limit: int, window: int) -> Tuple[bool, int]:
        now = self._clock()
        key = (bucket, identity)
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= now - window:
                hits.popleft()
            if len(hits) >= limit:
                retry_after = int(math.ceil(hits[0] + window - now))
                self._rejected += 1
                return False, max(retry_after, 1)
            hits.append(now)
            self._accepted += 1
            return True, 0

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "backend": self.backend,
                "shared_across_workers": False,
                "active_keys": len(self._hits),
                "tracked_hits": sum(len(v) for v in self._hits.values()),
                "accepted_total": self._accepted,
                "rejected_total": self._rejected,
            }

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
            self._rejected = 0
            self._accepted = 0


# ==============================================================================
# 2. الخلفية المشتركة في SQLite (الافتراضية للإنتاج)
# ==============================================================================
class SQLiteRateLimitStore(RateLimitStore):
    """
    نافذة منزلقة مشتركة بين كل العمليات على نفس المضيف:
      - WAL + busy_timeout لتحمّل التزامن بين العمال.
      - BEGIN IMMEDIATE يحوّل "عدّ ثم أدرج" إلى عملية ذرّية واحدة (لا سباق).
      - تنظيف دوري للصفوف الخارجة عن الأفق، مع حماية من قفزات الساعة للخلف.
    """

    backend = BACKEND_SQLITE

    def __init__(self, db_path=None, clock: Callable[[], float] = time.time,
                 cleanup_every: int = 500):
        self.db_path = str(db_path or os.getenv("CORESYNC_RATE_LIMIT_DB")
                           or (PROJECT_DIR / "sr_rate_limit.db"))
        self._clock = clock
        self._lock = threading.RLock()  # RLock: التنظيف يُستدعى داخل قفل hit
        self._cleanup_every = max(int(cleanup_every), 1)
        self._ops = 0
        self._accepted = 0
        self._rejected = 0
        self._conn = self._connect()
        self._init_schema()

    # --- التهيئة ---------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        # isolation_level=None: نتحكم في المعاملات صراحةً (BEGIN IMMEDIATE/COMMIT)
        con = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False,
                              isolation_level=None)
        con.execute("PRAGMA journal_mode = WAL;")
        con.execute("PRAGMA synchronous = NORMAL;")
        con.execute("PRAGMA busy_timeout = 5000;")
        return con

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS rate_hits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bucket TEXT NOT NULL,
                    identity TEXT NOT NULL,
                    ts REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_rate_hits_key
                    ON rate_hits(bucket, identity, ts);
                CREATE INDEX IF NOT EXISTS idx_rate_hits_ts
                    ON rate_hits(ts);
                """
            )

    # --- الحدّ -----------------------------------------------------------------
    def hit(self, bucket: str, identity: str, limit: int, window: int) -> Tuple[bool, int]:
        now = self._clock()
        cutoff = now - window
        with self._lock:
            con = self._conn
            try:
                con.execute("BEGIN IMMEDIATE")
                # نافذة منزلقة: نُسقط ما خرج عن النافذة (وأي طابع مستقبلي شاذ)
                con.execute(
                    "DELETE FROM rate_hits WHERE bucket = ? AND identity = ? "
                    "AND (ts <= ? OR ts > ?)",
                    (bucket, identity, cutoff, now + window),
                )
                row = con.execute(
                    "SELECT COUNT(*), MIN(ts) FROM rate_hits "
                    "WHERE bucket = ? AND identity = ?",
                    (bucket, identity),
                ).fetchone()
                count = int(row[0] or 0)
                oldest = row[1]

                if count >= limit:
                    con.execute("ROLLBACK")
                    self._rejected += 1
                    if oldest is None:
                        return False, max(int(window), 1)
                    retry_after = int(math.ceil(oldest + window - now))
                    return False, max(retry_after, 1)

                con.execute(
                    "INSERT INTO rate_hits (bucket, identity, ts) VALUES (?, ?, ?)",
                    (bucket, identity, now),
                )
                con.execute("COMMIT")
                self._accepted += 1
                self._ops += 1
                if self._ops % self._cleanup_every == 0:
                    self._cleanup(now)
                return True, 0
            except sqlite3.Error as exc:
                # فشل التخزين لا يُسقط الخدمة: نسمح ونسجّل (Fail-Open)
                try:
                    con.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
                logger.warning("تعذر تحديث عدّاد حدّ المعدل (%s): %s", self.db_path, exc)
                return True, 0

    def _cleanup(self, now: float) -> None:
        """إزالة الصفوف الخارجة عن الأفق حتى لا يتضخم الملف."""
        try:
            with self._lock:
                self._conn.execute(
                    "DELETE FROM rate_hits WHERE ts < ?",
                    (now - _CLEANUP_HORIZON_SECONDS,),
                )
        except sqlite3.Error as exc:  # التنظيف ليس حرجاً
            logger.warning("تعذر تنظيف عدّادات حدّ المعدل: %s", exc)

    # --- الإحصاءات --------------------------------------------------------------
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            try:
                row = self._conn.execute(
                    "SELECT COUNT(*), COUNT(DISTINCT identity) FROM rate_hits"
                ).fetchone()
                tracked, identities = int(row[0] or 0), int(row[1] or 0)
                error = None
            except sqlite3.Error as exc:
                tracked, identities, error = 0, 0, str(exc)
        payload = {
            "backend": self.backend,
            "shared_across_workers": True,
            "db_path": Path(self.db_path).name,
            "tracked_hits": tracked,
            "active_identities": identities,
            "accepted_total": self._accepted,
            "rejected_total": self._rejected,
        }
        if error:
            payload["error"] = error
        return payload

    def reset(self) -> None:
        with self._lock:
            try:
                self._conn.execute("DELETE FROM rate_hits")
            except sqlite3.Error as exc:
                logger.warning("تعذر تفريغ عدّادات حدّ المعدل: %s", exc)
            self._accepted = 0
            self._rejected = 0
            self._ops = 0

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.close()
            except sqlite3.Error:
                pass


# ==============================================================================
# 3. المصنع والمخزن الوحيد للعملية
# ==============================================================================
def create_rate_limit_store(backend: str = None, db_path: str = None) -> RateLimitStore:
    """
    إنشاء المخزن حسب البيئة، بتدرّج آمن:
      auto   → SQLite إن أمكن الكتابة، وإلا الذاكرة (مع تحذير).
      sqlite → نفس السلوك عند الفشل (توافرية الخدمة أولاً) مع تحذير صريح.
      memory → الذاكرة مباشرة.
    """
    chosen = (backend or os.getenv("CORESYNC_RATE_LIMIT_STORE", BACKEND_AUTO) or BACKEND_AUTO)
    chosen = str(chosen).strip().lower()
    if chosen not in VALID_BACKENDS:
        logger.warning("قيمة CORESYNC_RATE_LIMIT_STORE غير معروفة ('%s') — سيُستخدم auto", chosen)
        chosen = BACKEND_AUTO

    if chosen == BACKEND_MEMORY:
        return MemoryRateLimitStore()

    try:
        store = SQLiteRateLimitStore(db_path)
        logger.info("حدّ المعدل المشترك مفعّل عبر SQLite: %s", store.db_path)
        return store
    except Exception as exc:
        logger.error(
            "تعذر تهيئة مخزن حدّ المعدل المشترك (%s): %s — سيُستخدم مخزن الذاكرة "
            "(الحدّ سيكون لكل عامل على حدة).", db_path or "sr_rate_limit.db", exc,
        )
        return MemoryRateLimitStore()


_STORE: RateLimitStore = None


def get_rate_limit_store() -> RateLimitStore:
    """المخزن الوحيد للعملية (Singleton)."""
    global _STORE
    if _STORE is None:
        _STORE = create_rate_limit_store()
    return _STORE


def reset_rate_limit_store() -> None:
    """إعادة بناء المخزن (اختبارات، أو بعد تغيير البيئة)."""
    global _STORE
    if isinstance(_STORE, SQLiteRateLimitStore):
        _STORE.close()
    _STORE = None


__all__ = [
    "RateLimitStore",
    "MemoryRateLimitStore",
    "SQLiteRateLimitStore",
    "create_rate_limit_store",
    "get_rate_limit_store",
    "reset_rate_limit_store",
    "BACKEND_AUTO",
    "BACKEND_SQLITE",
    "BACKEND_MEMORY",
    "VALID_BACKENDS",
]
