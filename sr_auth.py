"""
==============================================================================
S&R CoreSync For Intelligent Solutions - Sovereign Platform
PROPRIETARY & CONFIDENTIAL INTELLECTUAL PROPERTY

Copyright (c) 2026 S&R CoreSync. All Rights Reserved.
Unauthorized copying, decompilation, redistribution, or external model training
of this file, via any medium, is strictly prohibited.
==============================================================================

==============================================================================
طبقة المصادقة والتحكم بالوصول والحد من المعدل (Security Remediation P0-1/P0-2)
==============================================================================
تعالج هذه الوحدة النتائج الحرجة التالية من التدقيق الأمني:
  - A1 (حرج): جميع نقاط النهاية كانت مكشوفة دون أي مصادقة أو تفويض.
  - A4 (مرتفع): CORS مفتوح على "*" مع allow_credentials=True.
  - A8 (متوسط): جلسات المحادثة بلا مالك؛ أي طرف يقرأ/يحذف جلسات الغير.

نموذج الأمان المعتمد:
  - مفاتيح API (X-API-Key أو Authorization: Bearer <key> أو ?api_key=<key> لقنوات
    SSE/WebSocket التي لا تستطيع تمرير ترويسات).
  - صلاحيات دقيقة (Fine-Grained Scopes) بصيغة <المورد>:<الإجراء> انظر
    sr_auth_advanced.ROUTE_PERMISSIONS: لكل مسار صلاحية محددة، ولكل مفتاح
    صلاحيات دوره الافتراضية أو تجاوز صريح، مع تاريخ انتهاء صلاحية (expires_at).
  - أدوار: admin (كل الصلاحيات) / writer / client / readonly.
  - الإغلاق الافتراضي (Fail-Closed): إن لم تُضبط أي مفاتيح تُرفض الطلبات المحمية
    بخطأ 503 ولا يعمل الخادم بشكل مفتوح أبداً.
  - مفتاح التطوير المحلي: CORESYNC_AUTH_DISABLED=1 (للاختبار على 127.0.0.1 فقط).
  - حد من المعدل (Sliding Window) في الذاكرة: افتراضياً 120 طلب/دقيقة، و10/دقيقة
    لمسارات استهلاك Gemini. ملاحظة: الحدّ هنا لكل عملية (worker)؛ للتوزيع المتعدد
    استخدم مخزناً مركزياً (Redis) — انظر دليل التطبيق.

المتغيرات البيئية:
  CORESYNC_API_KEYS        قائمة مفاتيح نصية مفصولة بفواصل بالصيغة: الاسم:المفتاح:الدور
                           مثال: ops-console:sk_live_xxx:admin,site-widget:sk_web_yyy:client
  CORESYNC_AUTH_FILE       مسار ملف JSON بالمفاتيح المُهشّرة (افتراضياً auth_keys.json)
  CORESYNC_AUTH_DISABLED   "1" لتعطيل المصادقة في التطوير المحلي فقط (يُسجّل تحذير)
  CORESYNC_RATE_LIMIT      الحد العام، مثال "120/min" (افتراضي 120/min)
  CORESYNC_CHAT_RATE_LIMIT حد مسارات المحادثة المكلفة، مثال "10/min" (افتراضي 10/min)
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs

from sr_rate_limit import RateLimitStore, get_rate_limit_store

from sr_auth_advanced import (
    ALL_PERMISSIONS,
    ROLE_ADMIN,
    ROLE_CLIENT,
    ROLE_PERMISSIONS,
    ROLE_READONLY,
    ROLE_WRITER,
    VALID_ROLES,
    WILDCARD,
    AdvancedKeyEntry,
    AdvancedKeyStore,
    hash_api_key,
    mask_digest,
    permissions_for_role,
    required_permission,
)

logger = logging.getLogger("sr_auth")

# ضبط الترميز لدعم العربية في الطرفية
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT_DIR = Path(__file__).resolve().parent

# أكواد إغلاق WebSocket (النطاق 4000-4999 محجوز للتطبيقات)
WS_CLOSE_UNAUTHORIZED = 4401
WS_CLOSE_FORBIDDEN = 4403
WS_CLOSE_NOT_CONFIGURED = 4503


# ==============================================================================
# 1. الهويات والأدوار (Principals & Roles)
# ==============================================================================
_VALID_ROLES = VALID_ROLES


class Principal:
    """
    هوية مستدعي مُصادق عليها (مفتاح API مرتبط باسم ودور وصلاحيات).
    الصلاحيات إمّا تجاوز صريح من المفتاح أو الافتراضي الخاص بدوره.
    """

    __slots__ = ("name", "role", "source", "permissions", "expires_at")

    def __init__(self, name: str, role: str, source: str = "api_key",
                 permissions: Optional[Tuple[str, ...]] = None,
                 expires_at: Optional[str] = None):
        self.name = name
        self.role = role if role in _VALID_ROLES else ROLE_CLIENT
        self.source = source
        self.permissions = (
            frozenset(permissions) if permissions is not None
            else permissions_for_role(self.role)
        )
        self.expires_at = expires_at

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    def has(self, permission: str) -> bool:
        """هل يملك هذا المستدعي صلاحية بعينها؟ (admin يملك كل شيء)"""
        if self.is_admin:
            return True
        return WILDCARD in self.permissions or permission in self.permissions

    def as_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "role": self.role,
            "source": self.source,
            "permissions": sorted(self.permissions),
            "expires_at": self.expires_at,
        }


# ==============================================================================
# 2. مخزن المفاتيح (Key Store) — واجهة رقيقة فوق AdvancedKeyStore
# ==============================================================================
class SovereignKeyStore:
    """
    واجهة متوافقة خلفياً حول AdvancedKeyStore: تحميل من ملف مهشّر و/أو متغير
    بيئة، مصادقة زمن-ثابت، وإدارة دورة حياة المفاتيح (إنشاء/إلغاء/دوران).
    """

    def __init__(self, auth_file: Optional[str] = None, persist: bool = True,
                 reload_interval: Optional[float] = None):
        if reload_interval is None:
            try:
                reload_interval = float(os.getenv("CORESYNC_AUTH_RELOAD_INTERVAL", "0.25"))
            except ValueError:
                reload_interval = 0.25
        self._advanced = AdvancedKeyStore(
            auth_file=auth_file, persist=persist, reload_interval=reload_interval
        )
        self.auth_file = self._advanced.auth_file

    # --- توافق خلفي -------------------------------------------------------------
    @staticmethod
    def hash_key(plain: str) -> str:
        return hash_api_key(plain)

    @property
    def auth_enabled(self) -> bool:
        return self._advanced.auth_enabled

    def __len__(self) -> int:
        return len(self._advanced)

    # --- المصادقة ---------------------------------------------------------------
    def authenticate(self, presented_key: str) -> Optional[Principal]:
        """مصادقة مفتاح بمقارنة زمن-ثابت؛ لا يكشف أي معلومة عند الفشل."""
        entry: Optional[AdvancedKeyEntry] = self._advanced.authenticate(presented_key)
        if entry is None:
            return None
        return Principal(
            name=entry.name,
            role=entry.role,
            permissions=tuple(entry.permission_set),
            expires_at=entry.expires_at,
        )

    @staticmethod
    def extract_key(raw_headers, query_string: bytes) -> Optional[str]:
        """استخراج المفتاح من الترويسات أو الاستعلام (لقنوات SSE/WebSocket)."""
        headers = dict(raw_headers or [])
        api_key = headers.get(b"x-api-key")
        if api_key:
            return api_key.decode("latin-1").strip()
        authorization = headers.get(b"authorization")
        if authorization:
            value = authorization.decode("latin-1").strip()
            if value.lower().startswith("bearer "):
                return value[7:].strip()
        if query_string:
            try:
                params = parse_qs(query_string.decode("latin-1"))
                values = params.get("api_key")
                if values and values[0].strip():
                    return values[0].strip()
            except Exception:
                pass
        return None

    # --- الإدارة ----------------------------------------------------------------
    def add_key(self, name: str, plain_key: Optional[str] = None, role: str = ROLE_CLIENT,
                expires_in_days: Optional[int] = None,
                permissions: Optional[List[str]] = None,
                metadata: Optional[Dict] = None,
                persist: bool = True) -> str:
        return self._advanced.add_key(
            name=name, plain_key=plain_key, role=role,
            expires_in_days=expires_in_days, permissions=permissions,
            metadata=metadata, persist=persist,
        )

    def revoke_key(self, key_sha256: str) -> bool:
        return self._advanced.revoke_key(key_sha256)

    def rotate_key(self, old_key_sha256: str, new_plain_key: Optional[str] = None) -> Optional[str]:
        return self._advanced.rotate_key(old_key_sha256, new_plain_key=new_plain_key)

    def get_key_info(self, key_sha256: str) -> Optional[Dict]:
        return self._advanced.get_key_info(key_sha256)

    def list_keys(self, include_revoked: bool = True) -> List[Dict]:
        return self._advanced.list_keys(include_revoked=include_revoked)

    def purge_expired(self, include_revoked: bool = False) -> int:
        return self._advanced.purge_expired(include_revoked=include_revoked)

    def flush_usage(self) -> bool:
        return self._advanced.flush_usage()

    def stats(self) -> Dict:
        return self._advanced.stats()


# مخزن وحيد مشترك بين الوسيلة ونقاط نهاية الإدارة (المفاتيح المُنشأة تعمل فوراً)
_KEY_STORE: Optional[SovereignKeyStore] = None


def get_key_store() -> SovereignKeyStore:
    """المخزن الوحيد للعملية (Singleton) بعد ضبط متغيرات البيئة."""
    global _KEY_STORE
    if _KEY_STORE is None:
        _KEY_STORE = SovereignKeyStore()
    return _KEY_STORE


def reset_key_store() -> None:
    """إعادة بناء المخزن (للاختبارات أو بعد تعديل متغيرات البيئة)."""
    global _KEY_STORE
    _KEY_STORE = None


# ==============================================================================
# 3. وسيلة المصادقة السيادية (Pure-ASGI Middleware) — إغلاق افتراضي
# ==============================================================================
# مسارات عامة لا تتطلب مصادقة (فحوص الجاهزية للوِب المحمل)
PUBLIC_PATHS = {"/", "/health"}


def _dev_principal() -> Principal:
    return Principal(name="local-dev", role=ROLE_ADMIN, source="auth_disabled")


class SovereignAuthMiddleware:
    """
    مصادقة جميع الطلبات المحمية على مستوى ASGI (HTTP + WebSocket)، مع الإغلاق
    الافتراضي وتفويض دقيق مبني على الصلاحيات:
      - 401 لمفتاح غائب/خاطئ/منتهٍ/ملغى.
      - 403 لمفتاح صحيح ينقصه صلاحية المسار المطلوبة.
      - 503 إن لم تُهيّأ أي مفاتيح على الإطلاق (فشل التهيئة، لا فتحٌ للخادم).
      - WebSocket: إغلاق بـ 4401/4403/4503 قبل قبول الاتصال.
    الهوية المُصادقة تُخزَّن في scope["state"]["principal"] لاستخدامها في
    نقاط النهاية (التحقق من ملكية الجلسات عبر get_principal).
    """

    def __init__(self, app, key_store: Optional[SovereignKeyStore] = None):
        self.app = app
        self.key_store = key_store or get_key_store()
        if not self.key_store.auth_enabled and os.getenv("CORESYNC_AUTH_DISABLED") != "1":
            logger.warning(
                "⚠️ لم تُضبط أي مفاتيح API (CORESYNC_API_KEYS أو CORESYNC_AUTH_FILE). "
                "سيرفض الخادم كل الطلبات المحمية برمز 503 حتى تُضبط المفاتيح. "
                "للتطوير المحلي فقط: CORESYNC_AUTH_DISABLED=1"
            )

    async def __call__(self, scope, receive, send):
        scope_type = scope.get("type")
        if scope_type not in ("http", "websocket"):
            return await self.app(scope, receive, send)

        is_ws = scope_type == "websocket"
        path = scope.get("path", "")
        method = "WS" if is_ws else scope.get("method", "GET").upper()

        # طلبات CORS المسبقة (OPTIONS) تُمرَّر لوسيلة CORS الخارجية دون مصادقة
        if not is_ws and method == "OPTIONS":
            return await self.app(scope, receive, send)

        # مسارات الصحة العامة فقط (HTTP)
        if not is_ws and path in PUBLIC_PATHS:
            return await self.app(scope, receive, send)

        # وضع التطوير المحلي الصريح (لن يعمل الخادم الإنتاجي هكذا)
        if not self.key_store.auth_enabled:
            if os.getenv("CORESYNC_AUTH_DISABLED") == "1":
                scope.setdefault("state", {})["principal"] = _dev_principal()
                return await self.app(scope, receive, send)
            await self._reject(
                send, is_ws, WS_CLOSE_NOT_CONFIGURED, 503,
                {
                    "status": "auth_not_configured",
                    "detail": "المصادقة غير مهيأة: اضبط CORESYNC_API_KEYS أو CORESYNC_AUTH_FILE قبل التشغيل.",
                },
            )
            return

        presented = self.key_store.extract_key(
            scope.get("headers") or [], scope.get("query_string", b"")
        )
        principal = self.key_store.authenticate(presented or "")
        if principal is None:
            await self._reject(
                send, is_ws, WS_CLOSE_UNAUTHORIZED, 401,
                {
                    "status": "unauthorized",
                    "detail": "مفتاح API مفقود أو غير صالح. مرّره عبر الترويسة X-API-Key أو Authorization: Bearer <key>",
                },
            )
            return

        # تفويض دقيق: صلاحية المسار المطلوبة (إن وُجدت)
        needed = required_permission(method, path)
        if needed and not principal.has(needed):
            await self._reject(
                send, is_ws, WS_CLOSE_FORBIDDEN, 403,
                {
                    "status": "forbidden",
                    "detail": f"هذه العملية تتطلب الصلاحية '{needed}'.",
                    "required_permission": needed,
                    "principal": principal.name,
                },
            )
            return

        scope.setdefault("state", {})["principal"] = principal
        return await self.app(scope, receive, send)

    async def _reject(self, send, is_ws: bool, ws_code: int, http_status: int, body: dict) -> None:
        """رفض موحّد: إغلاق WebSocket برمز تطبيقي أو استجابة JSON لـ HTTP."""
        if is_ws:
            await send({
                "type": "websocket.close",
                "code": ws_code,
                "reason": str(body.get("status", "unauthorized"))[:120],
            })
            return
        await self._send_json_error(send, http_status, body)

    async def _send_json_error(self, send, status: int, body: dict) -> None:
        import json as _json
        payload = _json.dumps(body, ensure_ascii=False).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(payload)).encode("latin-1")),
                (b"www-authenticate", b"ApiKey"),
            ],
        })
        await send({"type": "http.response.body", "body": payload})


# ==============================================================================
# 4. وسيلة الحد من المعدل (Sliding Window, في الذاكرة — لكل عملية worker)
# ==============================================================================
def _parse_rate(spec: str, default: Tuple[int, int]) -> Tuple[int, int]:
    """تحويل صيغة مثل '120/min' إلى (الحد، النافذة_بالثواني)"""
    try:
        value, _, unit = spec.strip().partition("/")
        limit = int(value)
        window = {"s": 1, "sec": 1, "m": 60, "min": 60, "h": 3600, "hour": 3600}.get(
            unit.strip().lower() or "min", 60
        )
        return limit, window
    except Exception:
        return default


class SovereignRateLimitMiddleware:
    """
    حدّ من المعدل بطبقتين، بنافذة منزلقة مشتركة بين كل العمال:

      1. **طبقة العنوان (الأساسية):** لكل IP — تحمي عدالة الاستخدام (زوار خلف
         نفس الـ NAT لا يستهلكون حصة غيرهم) وتصدّ الفيضان.
         الحدود: `CORESYNC_RATE_LIMIT` (عام) و`CORESYNC_CHAT_RATE_LIMIT` (محادثة).
      2. **سقف الاعتماد (الثانوية):** لكل مفتاح API (بصمة SHA-256، بلا تخزين للمفتاح)
         — يحمي حصة النموذج من استخدام موزّع عبر عناوين كثيرة لمفتاح مسرّب/مشترك.
         الحدود: `CORESYNC_KEY_RATE_LIMIT` و`CORESYNC_KEY_CHAT_RATE_LIMIT`
         (افتراضياً 10 أضعاف حدود العنوان).

    لماذا IP أولاً؟ لأن مفتاح الويدجت العام مشترك بين كل زوار الموقع؛ لو كان الحساب
    على المفتاح وحده لشارك كل الزوار حصة واحدة. ولماذا السقف ثانياً؟ لأن مفتاح
    شريك مسرّب قد يدور على عناوين لا نهائية. كلاهما يمرّ على نفس المخزن المشترك.
    """

    CHAT_PREFIXES = ("/api/chat", "/api/ai-concierge")

    def __init__(self, app, store: Optional[RateLimitStore] = None,
                 general: Optional[Tuple[int, int]] = None,
                 chat: Optional[Tuple[int, int]] = None,
                 key_general: Optional[Tuple[int, int]] = None,
                 key_chat: Optional[Tuple[int, int]] = None):
        self.app = app
        self.store = store if store is not None else get_rate_limit_store()
        general = general or _parse_rate(os.getenv("CORESYNC_RATE_LIMIT", "120/min"), (120, 60))
        chat = chat or _parse_rate(os.getenv("CORESYNC_CHAT_RATE_LIMIT", "10/min"), (10, 60))
        self.general_limit, self.general_window = general
        self.chat_limit, self.chat_window = chat
        # السقف لكل مفتاح: افتراضياً 10 أضعاف حدود العنوان
        self.key_general_limit, self.key_general_window = key_general or _parse_rate(
            os.getenv("CORESYNC_KEY_RATE_LIMIT", ""), (general[0] * 10, general[1])
        )
        self.key_chat_limit, self.key_chat_window = key_chat or _parse_rate(
            os.getenv("CORESYNC_KEY_CHAT_RATE_LIMIT", ""), (chat[0] * 10, chat[1])
        )

    def _client_ip(self, scope) -> str:
        client = scope.get("client")
        return client[0] if client else "unknown"

    @staticmethod
    def _presented_key(scope) -> Optional[str]:
        """استخراج المفتاح كما تفعل المصادقة، بلا أي تحقق أو تسجيل استخدام."""
        return SovereignKeyStore.extract_key(
            scope.get("headers") or [], scope.get("query_string", b"")
        )

    def _credential_identity(self, scope) -> Optional[str]:
        presented = self._presented_key(scope)
        if not presented:
            return None
        # بصمة مختصرة فقط: لا يُخزَّن المفتاح نفسه في جدول العدّادات
        return "cred:" + SovereignKeyStore.hash_key(presented)[:16]

    def _allow(self, name: str, identity: str, limit: int, window: int) -> Tuple[bool, int]:
        # النافذة جزء من اسم الحزمة: تغيير الإعداد لا يخلط عدّادات بنوافذ مختلفة
        return self.store.hit(f"{name}:{window}", identity, limit, window)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method", "GET").upper() == "OPTIONS":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        is_chat = path.startswith(self.CHAT_PREFIXES)

        # الطبقة 1: حصة العنوان (زائر/جهاز واحد)
        checks = [(
            "chat" if is_chat else "general",
            f"ip:{self._client_ip(scope)}",
            self.chat_limit if is_chat else self.general_limit,
            self.chat_window if is_chat else self.general_window,
        )]

        # الطبقة 2: سقف الاعتماد (المفتاح نفسه) إن قُدّم مفتاح
        credential = self._credential_identity(scope)
        if credential:
            checks.append((
                "key-chat" if is_chat else "key-general",
                credential,
                self.key_chat_limit if is_chat else self.key_general_limit,
                self.key_chat_window if is_chat else self.key_general_window,
            ))

        for bucket, identity, limit, window in checks:
            allowed, retry_after = self._allow(bucket, identity, limit, window)
            if not allowed:
                detail = (
                    "تجاوزت حد معدل المحادثة المسموح؛ حاول لاحقاً."
                    if is_chat else
                    "تجاوزت الحد العام لمعدل الطلبات؛ حاول لاحقاً."
                )
                await self._send_rate_limited(send, retry_after, detail)
                return

        return await self.app(scope, receive, send)

    async def _send_rate_limited(self, send, retry_after: int, detail: str) -> None:
        import json as _json
        payload = _json.dumps({"status": "rate_limited", "detail": detail}, ensure_ascii=False).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(payload)).encode("latin-1")),
                (b"retry-after", str(retry_after).encode("latin-1")),
            ],
        })
        await send({"type": "http.response.body", "body": payload})


# ==============================================================================
# 5. تبعيات FastAPI للوصول إلى الهوية وملكية الجلسات
# ==============================================================================
def get_principal(request) -> Principal:
    """تبعية FastAPI: استرجاع الهوية المُصادقة التي ضبطتها وسيلة المصادقة."""
    principal = getattr(request.state, "principal", None)
    if principal is None:
        # وصلنا إلى نقطة نهاية محمية دون وسيلة مصادقة (وضع التطوير المحلي)
        principal = _dev_principal()
    return principal


def principal_label(principal) -> str:
    """التسمية الآمنة للسجلات (بدون أي أسرار)"""
    return f"{principal.name}({principal.role})"


__all__ = [
    "Principal",
    "SovereignKeyStore",
    "SovereignAuthMiddleware",
    "SovereignRateLimitMiddleware",
    "get_key_store",
    "reset_key_store",
    "get_principal",
    "principal_label",
    "PUBLIC_PATHS",
    "ROLE_ADMIN",
    "ROLE_CLIENT",
    "ROLE_WRITER",
    "ROLE_READONLY",
    "ALL_PERMISSIONS",
    "ROLE_PERMISSIONS",
    "required_permission",
    "mask_digest",
]
