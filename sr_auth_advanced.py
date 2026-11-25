"""
==============================================================================
S&R CoreSync For Intelligent Solutions - Sovereign Platform
PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY
==============================================================================
إدارة مفاتيح API المتقدمة والصلاحيات الدقيقة (Advanced API Keys & Fine-Grained Scopes)
==============================================================================
يعالج هذا الملف ما كان ناقصاً في sr_auth.py:

  1. صلاحيات دقيقة (Fine-Grained Scopes) بصيغة <المورد>:<الإجراء> حيث الإجراء
     واحد من read / write / admin. الدور يمنح مجموعة افتراضية، ويمكن تجاوزها
     لكل مفتاح على حدة (مفتاح بصلاحيات محددة دون غيره).
  2. تاريخ انتهاء صلاحية (expires_at) لكل مفتاح، مع رفض المفتاح المنتهي فوراً
     وحتى لو بقي في الملف.
  3. خريطة مركزية للمسارات → الصلاحية المطلوبة (ROUTE_PERMISSIONS) تُستخدم في
     وسيلة المصادقة (HTTP و WebSocket) بدل قائمة مسارات إدارية مبهمة.
  4. إدارة كاملة لدورة حياة المفتاح: إنشاء (CSPRNG) / إلغاء / دوران / تطهير
     المنتهي، مع كتابة ذرّية للملف (os.replace) وصلاحيات 0600 على POSIX.
  5. إحصاءات استخدام في الذاكرة تُفرَّغ عند الطلب، بدل كتابة الملف في كل طلب
     (كانت كل مصادقة تكتب auth_keys.json إلى القرص).

المتغيرات البيئية:
  CORESYNC_AUTH_FILE       مسار ملف JSON بالمفاتيح المهشّرة (افتراضياً auth_keys.json)
                           الصيغة: {"keys":[{"name","key_sha256","role",
                                             "permissions","expires_at","is_revoked",
                                             "created_at","usage_count","last_used_at",
                                             "metadata"}]}
  CORESYNC_API_KEYS        مفاتيح نصية مفصولة بفواصل بالصيغة: الاسم:المفتاح:الدور
                           مثال: ops-console:sk_live_xxx:admin,site-widget:sk_web_yyy:client
  CORESYNC_KEY_TTL_DAYS    العمر الافتراضي للمفاتيح المُنشأة (0 أو غياب = بلا انتهاء)

تنبيه أمني: لا يُخزَّن أي مفتاح نصي (plaintext) في هذا الملف ولا في الملف الدائم؛
يُعاد النص مرة واحدة فقط لصاحبه لحظة الإنشاء أو الدوران.
"""

import os
import sys
import json
import hmac
import logging
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterable, List, NamedTuple, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("sr_auth_advanced")

PROJECT_DIR = Path(__file__).resolve().parent

# ==============================================================================
# 1. كتالوج الصلاحيات الدقيقة (Permission Catalog)
# ==============================================================================
# كل صلاحية = مورد:إجراء، والإجراء يبدأ من نطاقي read/write ويعلو إلى admin
# (list/delete/reindex/publish/run/keys...) حسب حساسية العملية.
SCOPE_READ = "read"
SCOPE_WRITE = "write"
SCOPE_ADMIN = "admin"

ALL_PERMISSIONS: FrozenSet[str] = frozenset({
    # المحادثة والمساعد الذكي
    "chat:read",
    "chat:write",
    # الجلسات والذاكرة
    "sessions:read",
    "sessions:write",
    "sessions:list",
    "sessions:delete",
    # ذاكرة المتجهات RAG
    "rag:read",
    "rag:write",
    "rag:reindex",
    # المرفقات والفهرسة
    "upload:write",
    # البث المباشر (SSE / WebSocket)
    "events:read",
    "events:publish",
    # منظومة الاستئناف والبوابة القانونية
    "appeals:read",
    "appeals:write",
    # وكيل التدقيق الذاتي
    "subagent:read",
    "subagent:run",
    # الإدارة
    "admin:keys",
    "admin:system",
})

# الأدوار ومجموعاتها الافتراضية. أي مفتاح قد يحمل تجاوزاً (override) خاصاً به.
ROLE_ADMIN = "admin"
ROLE_CLIENT = "client"
ROLE_READONLY = "readonly"
ROLE_WRITER = "writer"

ROLE_PERMISSIONS: Dict[str, FrozenSet[str]] = {
    # admin: كل الصلاحيات (ويشمل ضمنياً أي صلاحية تُضاف مستقبلاً)
    ROLE_ADMIN: ALL_PERMISSIONS,
    # writer: قراءة وكتابة تشغيلية بلا صلاحيات إدارة أو إعادة فهرسة كاملة
    ROLE_WRITER: frozenset({
        "chat:read", "chat:write",
        "sessions:read", "sessions:write",
        "rag:read", "rag:write",
        "upload:write",
        "events:read",
        "appeals:read", "appeals:write",
        "subagent:read",
    }),
    # client: واجهات الويب العامة (محادثة + قراءة معرفة) دون أي إدارة
    ROLE_CLIENT: frozenset({
        "chat:read", "chat:write",
        "sessions:read", "sessions:write",
        "rag:read",
        "events:read",
    }),
    # readonly: قراءة فقط (لوحات مراقبة، تقارير، بث)
    ROLE_READONLY: frozenset({
        "chat:read",
        "sessions:read",
        "rag:read",
        "events:read",
    }),
}

VALID_ROLES: FrozenSet[str] = frozenset(ROLE_PERMISSIONS)

# توافق خلفي: تمثيل قابل للتسلسل من نفس الكتالوج
PERMISSIONS: Dict[str, List[str]] = {
    role: sorted(perms) for role, perms in ROLE_PERMISSIONS.items()
}

# بدل كتابة "*" في قوائم مخزّنة، يُترجم دور admin إلى كل الصلاحيات + أي صلاحية مستقبلية
WILDCARD = "*"


def permissions_for_role(role: str) -> FrozenSet[str]:
    """الصلاحيات الافتراضية لدور؛ الدور غير المعروف يُعامل كـ client (إغلاق افتراضي)."""
    return ROLE_PERMISSIONS.get((role or "").strip().lower(), ROLE_PERMISSIONS[ROLE_CLIENT])


def has_permission(role: str, permission: str) -> bool:
    """هل يمنح الدور صلاحية بعينها؟ (توافق خلفي مع الاستخدام القديم)"""
    if (role or "").strip().lower() == ROLE_ADMIN:
        return True
    return permission in permissions_for_role(role)


def is_known_permission(permission: str) -> bool:
    return permission == WILDCARD or permission in ALL_PERMISSIONS


# ==============================================================================
# 2. خريطة المسارات → الصلاحيات المطلوبة (Route → Permission Map)
# ==============================================================================
class RouteRule(NamedTuple):
    method: str          # HTTP: GET/POST/DELETE | "WS" لاتصالات WebSocket
    path: str            # مسار تام أو بادئة
    permission: str      # الصلاحية المطلوبة
    prefix: bool = False  # True: مطابقة بالبادئة (للمسارات ذات المعاملات)


ROUTE_PERMISSIONS: Tuple[RouteRule, ...] = (
    # --- المحادثة والمساعد الذكي -------------------------------------------------
    RouteRule("POST", "/api/chat", "chat:write"),
    RouteRule("GET", "/api/chat/stream", "chat:write"),
    RouteRule("POST", "/api/ai-concierge", "chat:write"),
    RouteRule("GET", "/api/workspace/portals", "chat:read"),
    RouteRule("WS", "/ws/chat", "chat:write"),
    # --- الجلسات -----------------------------------------------------------------
    RouteRule("GET", "/api/sessions", "sessions:list"),
    RouteRule("GET", "/api/sessions/", "sessions:read", prefix=True),
    RouteRule("DELETE", "/api/sessions/", "sessions:delete", prefix=True),
    # --- ذاكرة المتجهات RAG --------------------------------------------------------
    RouteRule("GET", "/api/rag/search", "rag:read"),
    RouteRule("GET", "/api/rag/stats", "rag:read"),
    RouteRule("GET", "/api/rag/cache", "rag:read", prefix=True),
    RouteRule("DELETE", "/api/rag/cache", "rag:reindex"),
    RouteRule("POST", "/api/rag/reindex", "rag:reindex"),
    RouteRule("POST", "/api/upload", "upload:write"),
    # --- البث المباشر --------------------------------------------------------------
    RouteRule("GET", "/api/stream/events", "events:read"),
    RouteRule("WS", "/ws/events", "events:read"),
    RouteRule("POST", "/api/events/publish", "events:publish"),
    # --- وكيل التدقيق الذاتي -------------------------------------------------------
    RouteRule("GET", "/api/subagent/status", "subagent:read"),
    RouteRule("POST", "/api/subagent/run-audit", "subagent:run"),
    # --- البوابة القانونية والاستئناف ---------------------------------------------
    RouteRule("GET", "/api/counsel/", "appeals:read", prefix=True),
    RouteRule("GET", "/api/appeals/list", "appeals:read"),
    RouteRule("POST", "/api/appeals/lodge", "appeals:write"),
    # --- إدارة المفاتيح ------------------------------------------------------------
    RouteRule("GET", "/api/admin/keys", "admin:keys"),
    RouteRule("POST", "/api/admin/keys", "admin:keys"),
    RouteRule("POST", "/api/admin/keys/", "admin:keys", prefix=True),
    RouteRule("DELETE", "/api/admin/keys/", "admin:keys", prefix=True),
    RouteRule("GET", "/api/admin/system/rate-limit", "admin:system"),
)


def required_permission(method: str, path: str) -> Optional[str]:
    """
    الصلاحية المطلوبة لطلب ما، أو None إن كان المسار يتطلب مصادقة فقط.
    الأولوية: مطابقة تامة أولاً، ثم أطول بادئة مطابقة (لتفادي تعارض عام/خاص).
    """
    method = (method or "").upper()
    path = path or ""
    best: Optional[str] = None
    best_len = -1
    for rule in ROUTE_PERMISSIONS:
        if rule.method != method:
            continue
        if rule.prefix:
            if path.startswith(rule.path) and len(rule.path) > best_len:
                best, best_len = rule.permission, len(rule.path)
        elif path == rule.path:
            return rule.permission
    return best


# ==============================================================================
# 3. أدوات زمنية وتوليد المفاتيح
# ==============================================================================
def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso_utc(value: Optional[str]) -> Optional[datetime]:
    """
    تحليل طابع ISO إلى زمن واعٍ بالمنطقة الزمنية (UTC عند الغياب).
    يعيد None عند الفراغ أو القيمة غير الصالحة بدل رفع استثناء.
    """
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def generate_api_key(prefix: str = "sk_live") -> str:
    """توليد مفتاح API عشوائي آمن تشفيرياً (secrets) بدل الاختيار اليدوي."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def hash_api_key(plain_key: str) -> str:
    """بصمة SHA-256 لمفتاح نصي (الشكل الوحيد المخزَّن)."""
    return hashlib.sha256((plain_key or "").encode("utf-8")).hexdigest()


def mask_digest(digest: str, visible: int = 12) -> str:
    """عرض آمن للبصمة في السجلات والواجهات (لا يكشف المفتاح)."""
    digest = digest or ""
    return f"{digest[:visible]}…{digest[-4:]}" if len(digest) > visible + 4 else digest


# ==============================================================================
# 4. سجل مفتاح واحد (AdvancedKeyEntry)
# ==============================================================================
class AdvancedKeyEntry:
    """مفتاح API واحد: بصمة + دور + صلاحيات + انتهاء + إحصاء استخدام."""

    __slots__ = (
        "name", "role", "key_sha256", "expires_at", "permissions",
        "is_revoked", "created_at", "usage_count", "last_used_at", "metadata",
    )

    def __init__(self, name: str, role: str, key_sha256: str,
                 expires_at: Optional[str] = None,
                 permissions: Optional[Iterable[str]] = None,
                 is_revoked: bool = False,
                 created_at: Optional[str] = None,
                 usage_count: int = 0,
                 last_used_at: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.role = (role or ROLE_CLIENT).strip().lower()
        self.key_sha256 = key_sha256
        self.expires_at = expires_at
        # None = استخدام صلاحيات الدور الافتراضية، وقائمة = تجاوز صريح
        self.permissions: Optional[List[str]] = (
            sorted({p.strip() for p in permissions if p and p.strip()})
            if permissions is not None else None
        )
        self.is_revoked = bool(is_revoked)
        self.created_at = created_at or _utcnow().isoformat()
        self.usage_count = int(usage_count or 0)
        self.last_used_at = last_used_at
        self.metadata = metadata or {}

    # --- الاستعلام عن الحالة ---------------------------------------------------
    @property
    def permission_set(self) -> FrozenSet[str]:
        if self.permissions is not None:
            return frozenset(self.permissions)
        return permissions_for_role(self.role)

    def has_permission(self, permission: str) -> bool:
        if self.role == ROLE_ADMIN:
            return True
        return permission in self.permission_set

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        expires = parse_iso_utc(self.expires_at)
        if expires is None:
            # تاريخ تالف = مفتاح غير صالح (إغلاق افتراضي) وليس عمراً مفتوحاً
            logger.warning("تاريخ انتهاء غير صالح للمفتاح %s", self.name)
            return True
        return _utcnow() > expires

    def is_valid(self) -> bool:
        return not self.is_revoked and not self.is_expired()

    # --- التقادم والاستخدام -----------------------------------------------------
    def record_usage(self) -> None:
        self.usage_count += 1
        self.last_used_at = _utcnow().isoformat()

    def seconds_until_expiry(self) -> Optional[float]:
        expires = parse_iso_utc(self.expires_at)
        return None if expires is None else (expires - _utcnow()).total_seconds()

    # --- التسلسل ----------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """تمثيل التخزين الدائم (بلا أي مفتاح نصي)."""
        return {
            "name": self.name,
            "role": self.role,
            "key_sha256": self.key_sha256,
            "expires_at": self.expires_at,
            "permissions": self.permissions,
            "is_revoked": self.is_revoked,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
            "last_used_at": self.last_used_at,
            "metadata": self.metadata,
        }

    def to_public_dict(self) -> Dict[str, Any]:
        """تمثيل للإدارة/العرض: بصمة مقنّعة، حالة صريحة، الصلاحيات الفعالة."""
        return {
            "name": self.name,
            "role": self.role,
            "key_sha256": self.key_sha256,
            "key_masked": mask_digest(self.key_sha256),
            "permissions": sorted(self.permission_set),
            "permissions_overridden": self.permissions is not None,
            "is_revoked": self.is_revoked,
            "is_expired": self.is_expired(),
            "is_valid": self.is_valid(),
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "seconds_until_expiry": (
                round(self.seconds_until_expiry(), 1) if self.expires_at else None
            ),
            "usage_count": self.usage_count,
            "last_used_at": self.last_used_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdvancedKeyEntry":
        return cls(
            name=str(data.get("name", "unnamed")),
            role=str(data.get("role", ROLE_CLIENT)),
            key_sha256=str(data.get("key_sha256", "")),
            expires_at=data.get("expires_at"),
            permissions=data.get("permissions"),
            is_revoked=bool(data.get("is_revoked", False)),
            created_at=data.get("created_at"),
            usage_count=data.get("usage_count", 0),
            last_used_at=data.get("last_used_at"),
            metadata=data.get("metadata") or {},
        )


# ==============================================================================
# 5. مخزن المفاتيح المتقدم (AdvancedKeyStore)
# ==============================================================================
class AdvancedKeyStore:
    """
    مخزن مفاتيح مهشّرة مع إدارة كاملة للدورة الحياتية.

    ملاحظة أداء: المصادقة لا تكتب إلى القرص إطلاقاً؛ تُحدَّث العدادات في الذاكرة
    ويُعلَّم المخزن بـ dirty، ثم يُفرَّغ عند عملية إدارية أو عند إطفاء الخادم.
    """

    def __init__(self, auth_file: Optional[str] = None, persist: bool = True,
                 load_env: bool = True):
        self.auth_file = Path(auth_file) if auth_file else Path(
            os.getenv("CORESYNC_AUTH_FILE") or (PROJECT_DIR / "auth_keys.json")
        )
        self.persist = persist
        self._entries: Dict[str, AdvancedKeyEntry] = {}
        self._dirty = False
        self._load(load_env=load_env)

    # --- التحميل ----------------------------------------------------------------
    def _load(self, load_env: bool = True) -> None:
        # (أ) ملف JSON بالمفاتيح المهشّرة (المصدر الدائم)
        try:
            if self.auth_file.is_file():
                data = json.loads(self.auth_file.read_text(encoding="utf-8"))
                loaded = 0
                for entry_data in data.get("keys", []):
                    entry = AdvancedKeyEntry.from_dict(entry_data)
                    if len(entry.key_sha256) != 64:
                        logger.warning("تم تجاهل مفتاح ببصمة غير صالحة: %s", entry.name)
                        continue
                    self._entries[entry.key_sha256] = entry
                    loaded += 1
                if loaded:
                    logger.info("تم تحميل %d مفتاح API من %s", loaded, self.auth_file)
        except Exception as exc:  # ملف تالف لا يجب أن يفتح الخادم على مصراعيه
            logger.error("تعذر تحميل ملف المصادقة %s: %s", self.auth_file, exc)

        # (ب) مفاتيح من متغير البيئة (الأسرار السريعة/CD): الاسم:المفتاح:الدور
        if load_env:
            self._load_env_keys()

    def _load_env_keys(self) -> None:
        env_keys = os.getenv("CORESYNC_API_KEYS", "").strip()
        if not env_keys:
            return
        loaded = 0
        for spec in env_keys.split(","):
            parts = [p.strip() for p in spec.split(":") if p.strip()]
            if len(parts) < 2:
                continue
            name, plain = parts[0], parts[1]
            role = parts[2].lower() if len(parts) >= 3 else ROLE_CLIENT
            if role not in VALID_ROLES:
                logger.warning("مفتاح %s بدور غير معروف '%s' — سيُعامل كـ client", name, role)
                role = ROLE_CLIENT
            digest = hash_api_key(plain)
            # لا نطغى على تعريف ملف صريح لنفس البصمة
            self._entries.setdefault(
                digest, AdvancedKeyEntry(name=name, role=role, key_sha256=digest)
            )
            loaded += 1
        if loaded:
            logger.info("تم تحميل %d مفتاح من CORESYNC_API_KEYS", loaded)

    # --- الخصائص ----------------------------------------------------------------
    @property
    def auth_enabled(self) -> bool:
        return bool(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, key_sha256: object) -> bool:
        return key_sha256 in self._entries

    # --- الحفظ ------------------------------------------------------------------
    def save_to_file(self) -> None:
        """كتابة ذرّية: ملف مؤقت ثم os.replace حتى لا يبقى ملف نصف مكتوب."""
        self._dirty = False
        if not self.persist:
            return
        try:
            self.auth_file.parent.mkdir(parents=True, exist_ok=True)
            payload = {"keys": [e.to_dict() for e in self._entries.values()]}
            tmp_path = self.auth_file.with_name(self.auth_file.name + ".tmp")
            tmp_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            try:
                os.chmod(tmp_path, 0o600)
            except OSError:
                pass  # Windows لا يدعم نموذج POSIX؛ تُضبط الصلاحيات عبر NTFS ACL
            os.replace(tmp_path, self.auth_file)
            logger.info("تم حفظ %d مفتاح في %s", len(self._entries), self.auth_file)
        except Exception as exc:
            logger.error("تعذر حفظ ملف المصادقة %s: %s", self.auth_file, exc)

    def flush_usage(self) -> bool:
        """تفريغ عدادات الاستخدام المتراكمة في الذاكرة (إن تغيّرت)."""
        if self._dirty:
            self.save_to_file()
            return True
        return False

    # --- الإدارة ----------------------------------------------------------------
    def add_key(self, name: str, plain_key: Optional[str] = None, role: str = ROLE_CLIENT,
                expires_in_days: Optional[int] = None,
                expires_at: Optional[str] = None,
                permissions: Optional[Iterable[str]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                persist: bool = True) -> str:
        """
        إنشاء مفتاح جديد وإرجاع نصه مرة واحدة فقط.
        يرفع ValueError عند دور غير معروف أو صلاحية غير معروفة أو انتهاء غير صالح.
        """
        name = (name or "").strip()
        if not name:
            raise ValueError("اسم المفتاح مطلوب.")
        role = (role or ROLE_CLIENT).strip().lower()
        if role not in VALID_ROLES:
            raise ValueError(
                f"دور غير معروف: {role}. الأدوار المتاحة: {', '.join(sorted(VALID_ROLES))}"
            )

        explicit_perms: Optional[List[str]] = None
        if permissions is not None:
            explicit_perms = sorted({str(p).strip() for p in permissions if str(p).strip()})
            unknown = [p for p in explicit_perms if not is_known_permission(p)]
            if unknown:
                raise ValueError(f"صلاحيات غير معروفة: {', '.join(unknown)}")
            if not explicit_perms:
                raise ValueError("قائمة الصلاحيات فارغة؛ احذف المعامل لاستخدام صلاحيات الدور.")

        if expires_at is not None and parse_iso_utc(expires_at) is None:
            raise ValueError(f"تنسيق expires_at غير صالح: {expires_at}")

        if expires_at is None and expires_in_days is None:
            default_ttl = int(os.getenv("CORESYNC_KEY_TTL_DAYS", "0") or 0)
            expires_in_days = default_ttl or None

        if expires_at is None and expires_in_days is not None:
            if expires_in_days <= 0:
                raise ValueError("expires_in_days يجب أن يكون عدداً موجباً (أو حذفه لعدم الانتهاء).")
            expires_at = (_utcnow() + timedelta(days=int(expires_in_days))).isoformat()

        plain = (plain_key or "").strip() or generate_api_key()
        digest = hash_api_key(plain)
        if digest in self._entries:
            raise ValueError("المفتاح المُقدَّم موجود مسبقاً؛ استخدم الدوران (rotate) بدلاً من الإنشاء.")

        self._entries[digest] = AdvancedKeyEntry(
            name=name, role=role, key_sha256=digest, expires_at=expires_at,
            permissions=explicit_perms, metadata=metadata or {},
        )
        if persist:
            self.save_to_file()
        logger.info("تمت إضافة مفتاح: %s (الدور: %s)", name, role)
        return plain

    def revoke_key(self, key_sha256: str) -> bool:
        entry = self._entries.get(key_sha256)
        if entry is None:
            return False
        if not entry.is_revoked:
            entry.is_revoked = True
            self.save_to_file()
        logger.info("تم إلغاء المفتاح: %s (الاسم: %s)", mask_digest(key_sha256), entry.name)
        return True

    def revoke_by_name(self, name: str) -> int:
        count = 0
        for entry in self._entries.values():
            if entry.name == name and not entry.is_revoked:
                entry.is_revoked = True
                count += 1
        if count:
            self.save_to_file()
        return count

    def rotate_key(self, old_key_sha256: str, new_plain_key: Optional[str] = None,
                   keep_permissions: bool = True) -> Optional[str]:
        """
        دوران المفتاح: يُحذف القديم ويُنشأ جديد بنفس الاسم والدور والصلاحيات
        والانتهاء. يعيد المفتاح الجديد (مرة واحدة) أو None إن لم يوجد القديم.
        """
        old = self._entries.get(old_key_sha256)
        if old is None:
            return None
        if not old.is_valid():
            raise ValueError("لا يمكن دوران مفتاح ملغى أو منتهٍ؛ أنشئ مفتاحاً جديداً.")

        new_plain = (new_plain_key or "").strip() or generate_api_key()
        new_digest = hash_api_key(new_plain)
        if new_digest in self._entries:
            raise ValueError("المفتاح الجديد مستخدم مسبقاً.")

        metadata = dict(old.metadata or {})
        metadata["rotated_from"] = mask_digest(old_key_sha256)
        metadata["rotated_at"] = _utcnow().isoformat()

        self._entries[new_digest] = AdvancedKeyEntry(
            name=old.name,
            role=old.role,
            key_sha256=new_digest,
            expires_at=old.expires_at,
            permissions=old.permissions if keep_permissions else None,
            metadata=metadata,
        )
        del self._entries[old_key_sha256]
        self.save_to_file()
        logger.info("تم دوران المفتاح: %s", old.name)
        return new_plain

    def purge_expired(self, include_revoked: bool = False) -> int:
        """إزالة المفاتيح المنتهية (واختيارياً الملغاة) من الملف."""
        stale = [
            sha for sha, entry in self._entries.items()
            if entry.is_expired() or (include_revoked and entry.is_revoked)
        ]
        for sha in stale:
            del self._entries[sha]
        if stale:
            self.save_to_file()
        return len(stale)

    # --- القراءة ----------------------------------------------------------------
    def get_entry(self, key_sha256: str) -> Optional[AdvancedKeyEntry]:
        return self._entries.get(key_sha256)

    def list_entries(self, include_revoked: bool = True) -> List[AdvancedKeyEntry]:
        entries = list(self._entries.values())
        if not include_revoked:
            entries = [e for e in entries if e.is_valid()]
        return sorted(entries, key=lambda e: e.created_at or "")

    def list_keys(self, include_revoked: bool = True) -> List[Dict[str, Any]]:
        return [e.to_public_dict() for e in self.list_entries(include_revoked=include_revoked)]

    def get_key_info(self, key_sha256: str) -> Optional[Dict[str, Any]]:
        entry = self._entries.get(key_sha256)
        return entry.to_public_dict() if entry else None

    # --- المصادقة ---------------------------------------------------------------
    def authenticate(self, presented_key: str) -> Optional[AdvancedKeyEntry]:
        """
        مصادقة مفتاح مقدَّم بمقارنة زمن-ثابت (hmac.compare_digest).
        يعيد None للمفقود/الخاطئ/الملغى/المنتهي دون كشف السبب.
        """
        if not presented_key:
            return None
        digest = hash_api_key(presented_key)
        for candidate, entry in self._entries.items():
            if hmac.compare_digest(candidate, digest):
                if not entry.is_valid():
                    logger.warning(
                        "محاولة استخدام مفتاح %s (%s): revoked=%s expired=%s",
                        mask_digest(candidate), entry.name, entry.is_revoked, entry.is_expired(),
                    )
                    return None
                entry.record_usage()
                self._dirty = True
                return entry
        return None

    # --- الإحصاءات ---------------------------------------------------------------
    def stats(self) -> Dict[str, Any]:
        entries = list(self._entries.values())
        return {
            "total_keys": len(entries),
            "valid_keys": sum(1 for e in entries if e.is_valid()),
            "revoked_keys": sum(1 for e in entries if e.is_revoked),
            "expired_keys": sum(1 for e in entries if e.is_expired()),
            "roles": {role: sum(1 for e in entries if e.role == role) for role in sorted(VALID_ROLES)},
            "auth_file": str(self.auth_file),
            "persisted": self.persist,
            "pending_usage_flush": self._dirty,
        }
