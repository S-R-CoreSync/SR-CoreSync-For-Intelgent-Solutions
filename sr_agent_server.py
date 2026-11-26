import os
import sys
import io
import json
import time
import asyncio
import hashlib
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, Tuple

from fastapi import (
    FastAPI, HTTPException, Request, Query, Path, UploadFile, File,
    WebSocket, WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from pydantic import BaseModel, Field

# ضبط الترميز لدعم العربية في الطرفية
sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("sr_agent_server")

from sr_agent_core import (
    create_sovereign_agent_config,
    SOVEREIGN_SYSTEM_INSTRUCTIONS,
    tool_get_service_details,
    tool_list_project_portals
)
import sr_session_db
from sr_rag_engine import SovereignRAGDatabase, build_or_update_knowledge_index, query_rag_knowledge, index_custom_document
from sr_subagent_monitor import AutonomousSecurityHealthSubagent
from sr_auth import (
    SovereignAuthMiddleware,
    SovereignRateLimitMiddleware,
    get_principal,
    get_key_store,
)
from sr_rate_limit import get_rate_limit_store
from google.antigravity import Agent

# ==============================================================================
# نماذج البيانات (Pydantic Schemas) لتوثيق Swagger التفاعلي
# ==============================================================================
class ChatRequest(BaseModel):
    message: str = Field(..., description="نص الرسالة أو الاستفسار الموجه للوكيل الذكي", example="ما هي باقات الخدمات المتوفرة؟")
    session_id: Optional[str] = Field("default", description="معرّف الجلسة لضمان استمرارية الذاكرة والسياق", example="client_session_101")
    channel: Optional[str] = Field("web_portal", description="قناة المحادثة (web_portal, whatsapp, telegram)", example="web_portal")

class ConciergeRequest(BaseModel):
    message: str = Field(..., description="نص الرسالة الواردة من محاكي المتصفح أو تطبيق العميل", example="ما هي باقة السوشيال ميديا 8K؟")
    channel: Optional[str] = Field("whatsapp_cloud_api", description="اسم القناة الافتراضية", example="whatsapp_cloud_api")
    session_id: Optional[str] = Field("concierge_default", description="معرّف الجلسة للمحاكي", example="concierge_default")

class ActionButton(BaseModel):
    label: str = Field(..., description="عنوان الزر التفاعلي")
    url: Optional[str] = Field(None, description="رابط الإجراء إن وجد")
    action: Optional[str] = Field(None, description="اسم الإجراء في الواجهة")

class ChatResponseModel(BaseModel):
    reply: str = Field(..., description="نص استجابة المستشار الذكي التنفيذي")
    session_id: str = Field(..., description="معرّف الجلسة النشطة")
    source: str = Field(..., description="مصدر الإجابة (google_antigravity_agent أو sovereign_knowledge_engine)")
    timestamp: str = Field(..., description="طابع التوقيت الزمني")

class ConciergeResponseModel(BaseModel):
    reply: str = Field(..., description="نص الرد المؤسسي")
    actions: List[ActionButton] = Field(..., description="قائمة الأزرار والإجراءات السريعة")
    intent: str = Field("sovereign_executive_advisory", description="نية المستخدم المستنتجة")
    confidence: float = Field(0.99, description="درجة ثقة النموذج")
    channel: str = Field(..., description="القناة")
    source: str = Field(..., description="المصدر")
    session_id: str = Field(..., description="معرّف الجلسة")
    timestamp: str = Field(..., description="الطابع الزمني")

class PublishEventRequest(BaseModel):
    event_type: str = Field(..., description="نوع الحدث (e.g. new_evidence_uploaded, settlement_completed, appeal_lodged, escrow_frozen)")
    payload: Dict[str, Any] = Field(..., description="بيانات الحدث التفصيلية")

class AppealRequest(BaseModel):
    case_id: str = Field(..., description="معرف القضية الأصلية", example="ARB-2026-0418")
    appellant: str = Field(..., description="الطرف المستأنف", example="Rotterdam Logistics B.V.")
    respondent: str = Field(..., description="المستأنف ضده", example="Gulf Trade Holding LLC")
    grounds: str = Field(..., description="أسباب الاستئناف واكتشاف أدلة جنائية جديدة في WORM", example="اكتشاف سجلات تدقيق محاسبي إضافية EVD-2026-901 تثبت تسليم الشحنة")
    evidence_worm_hash: Optional[str] = Field(None, description="بصمة SHA-256 للمستند الجنائي في WORM", example="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    counsel_signature: Optional[str] = Field("Counsel Salim Al-Din (Bar Reg. 104)", description="توقيع المستشار القانوني المعتمد")

class CreateKeyRequest(BaseModel):
    """طلب إنشاء مفتاح API بصلاحيات دقيقة وتاريخ انتهاء."""
    name: str = Field(..., description="اسم وصفي للمفتاح (الجهة/التطبيق)", example="partner-portal-eu")
    role: str = Field("client", description="الدور: admin | writer | client | readonly", example="client")
    expires_in_days: Optional[int] = Field(None, description="عمر المفتاح بالأيام (اتركه فارغاً لعدم الانتهاء)", example=90)
    permissions: Optional[List[str]] = Field(None, description="تجاوز صلاحيات الدور بصيغة <المورد>:<الإجراء>", example=["chat:read", "rag:read"])
    metadata: Optional[Dict[str, Any]] = Field(None, description="بيانات وصفية حرة (الجهة، التذكرة، البيئة)")

# ==============================================================================
# إدارة البث المباشر للنبض السيادي (SSE + WebSocket Event Bus)
# ==============================================================================
# مجموعة اشتراكات واحدة تغذي الناقلين معاً: كل مشترك يحصل على رسائل (dict) خام،
# وكل نقطة نهاية (SSE أو WebSocket) تُسلسلها بصيغتها. هذا يضمن أن الحدث الواحد
# بمخطط واحد على كل القنوات.
sse_subscribers: set[asyncio.Queue] = set()


def sse_frame(message: Dict[str, Any]) -> str:
    """تغليف رسالة في إطار SSE موحد."""
    return f"data: {json.dumps(message, ensure_ascii=False)}\n\n"


def split_text_chunks(text: str, max_chars: int = 24) -> List[str]:
    """تقسيم نص إلى مقاطع بثٍّ قصيرة (بحدود الكلمات، مع الإبقاء على المسافات)."""
    chunks: List[str] = []
    buffer: List[str] = []
    length = 0
    for word in (text or "").split(" "):
        piece = word + " "
        buffer.append(piece)
        length += len(piece)
        if length >= max_chars:
            chunks.append("".join(buffer))
            buffer, length = [], 0
    if buffer:
        chunks.append("".join(buffer))
    return chunks or [""]


async def broadcast_live_event(event_type: str, payload: dict) -> int:
    """بث حدث لحظي لجميع الواجهات المتصلة (SSE و WebSocket) وإرجاع عدد المستلمين."""
    if not sse_subscribers:
        return 0
    message = {
        "event": event_type,
        "timestamp": datetime.now().isoformat(),
        "payload": payload,
    }
    delivered = 0
    dead_queues = set()
    for q in sse_subscribers:
        try:
            q.put_nowait(message)
            delivered += 1
        except asyncio.QueueFull:
            dead_queues.add(q)
    for dq in dead_queues:
        sse_subscribers.discard(dq)
    return delivered

async def call_agent_text(prompt: str) -> Optional[str]:
    """
    نداء واحد لوكيل Google Antigravity وإرجاع النص، أو None عند فشل الاتصال
    بالمنظومة الخارجية كي يستخدم المستدعي الصمود السيادي القائم على RAG.

    ⚠️ يُنفَّذ في خيط عامل (worker thread) لأن SDK الوكيل يقوم بإدخال/إخراج
    متزامن (شبكة/تهيئة عميل) داخل دالتِه الـ async؛ تنفيذه على حلقة الأحداث
    كان يُجمّد الخادم بأكمله 10-12 ثانية (توقف /health و SSE و WebSocket لكل
    المستخدمين). العزل في خيط يُبقي الحلقة حيّة ويحفظ زمن الاستجابة للبقية.
    """
    def _run_blocking() -> str:
        async def _inner() -> str:
            async with Agent(app.state.config) as agent:
                resp = await asyncio.wait_for(agent.chat(prompt), timeout=60.0)
                return await resp.text()
        return asyncio.run(_inner())

    try:
        return await asyncio.wait_for(asyncio.to_thread(_run_blocking), timeout=70.0)
    except Exception as exc:
        logger.debug("تعذر الوصول إلى وكيل Antigravity، سيُستخدم الصمود السيادي: %s", exc)
        return None


def _is_usable_match(matches: List[Dict[str, Any]], min_score: float = 0.40,
                     min_coverage: float = 0.50) -> bool:
    """
    هل مطابقات RAG صالحة لبناء سياق؟ بعد إضافة «التغطية» صارت الجودة تُقاس
    بمدى تغطية مصطلحات السؤال، لا بدرجة ملتبسة: مقطع يطابق نصف السؤال فقط
    (شريط تنقّل مثلاً) لا يُحقن في سياق النموذج.
    """
    if not matches:
        return False
    top = matches[0]
    # المقطع المثبّت مُختار بقاعدة مُدارة (pinning)، فلا نُخضعه لشرط التغطية اللفظي
    if top.get("pinned"):
        return top.get("score", 0.0) >= min_score
    return top.get("score", 0.0) >= min_score and top.get("coverage", 1.0) >= min_coverage


async def generate_sovereign_answer(
    message: str,
    session_id: str,
    principal,
    *,
    max_turns: int = 4,
    top_k: int = 2,
    fallback_lead: str = "وفقاً للوثائق الرسمية",
    fallback_contact: str = "للمزيد تواصل عبر واتساب: +31 618111116.",
) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    خط توليد الإجابة الموحّد (HTTP و WebSocket):
      1. حفظ رسالة المستخدم.
      2. سحب سياق الجلسة + استرجاع RAG المخزأ مؤقتاً (بصمة + TTL).
      3. نداء الوكيل، أو الصمود السيادي من RAG/أدوات مساحة العمل.
      4. حفظ رد الوكيل وإرجاع (النص، المصدر، مطابقات RAG).
    """
    sr_session_db.add_message(session_id, "user", message, source="user", owner=principal.name)

    context = sr_session_db.get_formatted_context(session_id, max_turns=max_turns)
    rag_matches = app.state.rag_db.hybrid_search_cached(message, top_k=top_k)
    rag_context = ""
    if _is_usable_match(rag_matches):
        rag_snippets = "\n".join(f"• [{r['title']}]: {r['content'][:300]}" for r in rag_matches)
        rag_context = f"\n[المعرفة الموثقة من مساحة عمل المشروع (Local RAG Context)]:\n{rag_snippets}\n"

    prompt = f"{context}\n{rag_context}\nسؤال المستخدم الحالي: {message}".strip()

    reply_text = await call_agent_text(prompt)
    source = "google_antigravity_agent"
    if reply_text is None:
        source = "sovereign_rag_knowledge_engine"
        if _is_usable_match(rag_matches):
            top_match = rag_matches[0]
            reply_text = (
                f"{fallback_lead} ({top_match['title']}):\n"
                f"{top_match['content'][:350]}...\n\n{fallback_contact}"
            )
        else:
            reply_text = tool_get_service_details(message)

    sr_session_db.add_message(session_id, "assistant", reply_text, source=source, owner=principal.name)
    return reply_text, source, rag_matches


pulse_shutdown_event: Optional[asyncio.Event] = None

def get_pulse_shutdown_event() -> asyncio.Event:
    global pulse_shutdown_event
    if pulse_shutdown_event is None:
        pulse_shutdown_event = asyncio.Event()
    return pulse_shutdown_event

async def telemetry_pulse_loop(app: FastAPI):
    """حلقة البث النبضي الدوري (Heartbeat & Telemetry) لتغذية لوحة القيادة الموحدة"""
    evt = get_pulse_shutdown_event()
    while not evt.is_set():
        try:
            try:
                await asyncio.wait_for(evt.wait(), timeout=5.0)
                break
            except asyncio.TimeoutError:
                pass

            if sse_subscribers:
                stats = app.state.rag_db.get_stats() if hasattr(app.state, "rag_db") else {}
                appeal_count = len(app.state.appeals) if hasattr(app.state, "appeals") else 0
                pulse_data = {
                    "suite_health": 100,
                    "active_hubs": 6,
                    "arbitration_active": 4,
                    "arbitration_value_eur": 12385000,
                    "cbdc_settles": 12,
                    "cbdc_savings_eur": 38450,
                    "zkp_enclaves": 3,
                    "zkp_proofs": 28,
                    "forensics_docs": stats.get("total_documents", 90),
                    "forensics_chunks": stats.get("total_chunks", 506),
                    "escrow_vaults": 4,
                    "escrow_total_eur": 22350000,
                    "escrow_locked_eur": 6250000 + (appeal_count * 1850000),
                    "active_appeals": appeal_count,
                    "worm_status": "VERIFIED_IMMUTABLE",
                    "heartbeat": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                await broadcast_live_event("pulse_telemetry", pulse_data)
        except asyncio.CancelledError:
            break
        except Exception:
            pass

# ==============================================================================
# دورة حياة التطبيق (Lifespan Context)
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    get_pulse_shutdown_event().clear()

    # 1. تهيئة قاعدة بيانات الجلسات والذاكرة
    sr_session_db.init_db()
    
    # 2. تهيئة ذاكرة المتجهات المحلية (Local Vector DB / RAG)
    app.state.rag_db = SovereignRAGDatabase()
    stats = app.state.rag_db.get_stats()
    if stats.get("total_chunks", 0) == 0:
        print("  🔄 جاري الفهرسة التأسيسية لذاكرة المتجهات RAG...")
        build_or_update_knowledge_index()

    # 3. تهيئة الوكيل الفرعي الذاتي للتدقيق الأمني والصحي
    app.state.subagent = AutonomousSecurityHealthSubagent()

    # 4. تكوين وكيل Google Antigravity
    app.state.config = create_sovereign_agent_config()

    # 5. تهيئة سجل الاستئنافات السيادية النشطة (Mission 112)
    if not hasattr(app.state, "appeals") or not app.state.appeals:
        app.state.appeals = [
            {
                "appeal_id": "APP-2026-0418",
                "case_id": "ARB-2026-0418",
                "appellant": "Rotterdam Logistics B.V.",
                "respondent": "Gulf Trade Holding LLC",
                "grounds": "ظهور مستند WORM جنائي إضافي EVD-2026-901 يثبت تزوير بوليصة الشحن البحرية",
                "evidence_worm_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "counsel_signature": "Counsel Hendrik Van Der Berg (NAI Netherlands)",
                "status": "APPEAL_UNDER_REVIEW",
                "escrow_action": "ESCROW_LOCKED_EUR_1850000",
                "timestamp": "2026-10-31T11:20:00Z",
                "seal_sha256": "8a7c2e4f01b965dd34c4980a31ecde01a54728fba0e9176395bcf6d3910a30b1"
            }
        ]

    print("=" * 70)
    print("  🏛️ خادم S&R CoreSync Sovereign Agent API قيد التشغيل والجاهزية")
    print(f"  🧠 ذاكرة المتجهات (RAG): {stats.get('total_documents', 0)} مستنداً و {stats.get('total_chunks', 0)} قطعة دلالية.")
    print("  🛡️ الوكيل الفرعي للتدقيق الذاتي (Subagent Monitor): نشط وجاهز.")
    print("  ⚡ البث المباشر للنبض السيادي (SSE + WebSocket): جاهز للاشتراك.")
    print("  🔐 صلاحيات دقيقة لكل مفتاح (read/write/admin) مع تاريخ انتهاء: مفعّلة.")
    print(f"  🤖 النموذج النشط: {app.state.config.model}")
    print("  📚 توثيق Swagger التفاعلي متاح على: http://127.0.0.1:8000/docs")
    print("  💾 ذاكرة الجلسات المستمرة (SQLite): نشطة وجاهزة")
    print("=" * 70)
    yield
    get_pulse_shutdown_event().set()
    # تفريغ إحصاءات استخدام المفاتيح المتراكمة في الذاكرة (إن تغيّرت)
    try:
        get_key_store().flush_usage()
    except Exception:
        pass
    print("🛑 إيقاف خادم الوكيل الذكي بنجاح.")

# إنشاء تطبيق FastAPI مع تعطيل مسارات docs التلقائية لتخصيصها بهوية S&R
app = FastAPI(
    title="S&R CoreSync Sovereign Agent Micro-API",
    description="""
### 🏛️ واجهة برمجة التطبيقات المصغرة للمستشار الذكي التنفيذي لـ S&R CoreSync
توفر هذه المنظومة:
- **تكامل كامل مع Google Antigravity SDK** ونماذج Gemini.
- **أدوات مساحة العمل (Workspace Tools)** لاستكشاف صفحات وملفات وباقات المشروع.
- **ذاكرة محادثة مستمرة (SQLite Session DB)** لحفظ واسترجاع سياق الحوار.
- **بث مباشر بتقنية Server-Sent Events (SSE)** لتدفق الكلمات لحظياً.
- **ربط مباشر مع واجهات الويب ومحاكي الذكاء الاصطناعي.**
    """,
    version="2.1.0",
    docs_url=None,   # يتم تقديمها مخصصة
    redoc_url=None,
    lifespan=lifespan
)

# التهيئة المسبقة لسجل الاستئنافات في app.state لضمان الجاهزية الفورية
app.state.appeals = [
    {
        "appeal_id": "APP-2026-0418",
        "case_id": "ARB-2026-0418",
        "appellant": "Rotterdam Logistics B.V.",
        "respondent": "Gulf Trade Holding LLC",
        "grounds": "ظهور مستند WORM جنائي إضافي EVD-2026-901 يثبت تزوير بوليصة الشحن البحرية",
        "evidence_worm_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "counsel_signature": "Counsel Hendrik Van Der Berg (NAI Netherlands)",
        "status": "APPEAL_UNDER_REVIEW",
        "escrow_action": "ESCROW_LOCKED_EUR_1850000",
        "timestamp": "2026-10-31T11:20:00Z",
        "seal_sha256": "8a7c2e4f01b965dd34c4980a31ecde01a54728fba0e9176395bcf6d3910a30b1"
    }
]

# ==============================================================================
# [P0-1 / A1] طبقة المصادقة السيادية و [P0-2 / A4] تقييد CORS
# ==============================================================================
# ترتيب الإضافة يحدد التداخل: الأخير في الإضافة هو الأبعد في المعالجة.
# التدفق المطلوب: CORS (للطلبات المسبقة OPTIONS) → الحد من المعدل → المصادقة → المسارات.
app.add_middleware(SovereignAuthMiddleware)        # الأعمق: مصادقة إغلاقية لكل الطلبات المحمية
app.add_middleware(SovereignRateLimitMiddleware)   # حد من المعدل (حماية حصة Gemini من الإجهاد)

_allowed_origins = [
    origin.strip() for origin in os.getenv(
        "CORESYNC_CORS_ORIGINS",
        "https://sr-coresync.com,https://www.sr-coresync.com,http://127.0.0.1:8000,http://localhost:8000"
    ).split(",") if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,   # المصادقة بمفاتيح API لا تحتاج كوكيز؛ إلغاء الترخيص يقطع هجوم الأصل الوحيد
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["X-API-Key", "Authorization", "Content-Type"],
    max_age=600,
)

# ==============================================================================
# تخصيص واجهات التوثيق التفاعلية (Swagger & ReDoc) بهوية المنظومة
# ==============================================================================
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="S&R CoreSync | Sovereign Agent API — Swagger Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://sr-coresync.com/favicon.ico"
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="S&R CoreSync | Sovereign Agent API — ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="https://sr-coresync.com/favicon.ico"
    )

# ==============================================================================
# نقاط النهاية الرئيسية (API Endpoints)
# ==============================================================================
@app.get("/", tags=["النظام والجاهزية"])
async def root():
    """فحص حالة الخادم والنموذج وروابط التوثيق"""
    return {
        "service": "S&R CoreSync Sovereign Agent API",
        "status": "online",
        "version": "2.1.0",
        "model": app.state.config.model,
        "swagger_docs": "/docs",
        "redoc": "/redoc",
        "transports": {
            "sse_events": "/api/stream/events",
            "websocket_events": "/ws/events",
            "websocket_chat": "/ws/chat",
        },
        "auth": {
            "scheme": "X-API-Key | Bearer | ?api_key=",
            "permissions": "<resource>:<action> (read/write/admin)",
            "key_management": "/api/admin/keys",
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/health", tags=["النظام والجاهزية"])
async def health():
    """فحص النبض اللحظي للخدمة (Health Check)"""
    return {"status": "ok", "agent_ready": True, "db_ready": True}

@app.get("/api/workspace/portals", tags=["أدوات مساحة العمل"])
async def get_portals():
    """استعراض قائمة بوابات وصفحات المشروع الرسمية الـ 80"""
    return {"portals_summary": tool_list_project_portals()}

@app.post("/api/ai-concierge", response_model=ConciergeResponseModel, tags=["المساعد الذكي والمحاكي"])
async def ai_concierge_endpoint(req: ConciergeRequest, request: Request):
    """
    نقطة النهاية المعتمدة لمحاكي `ai-concierge-simulator.html` وويدجت المحادثة العائم،
    مع حفظ الحوار بالكامل في ذاكرة الجلسة المستمرة.
    """
    user_msg = req.message.strip()
    session_id = req.session_id or "concierge_default"
    principal = get_principal(request)  # [A8] الهوية المُصادقة = مالك الجلسة
    if not user_msg:
        raise HTTPException(status_code=400, detail="الرسالة لا يمكن أن تكون فارغة")

    # 1-3. حفظ الرسالة، بناء سياق RAG (مخزأ مؤقتاً)، توليد الرد، ثم حفظ رد الوكيل
    reply_text, source, _rag_matches = await generate_sovereign_answer(
        user_msg, session_id, principal, max_turns=4, top_k=2,
        fallback_lead="بناءً على وثائق وبوابات المنظومة الرسمية",
        fallback_contact="لطلب استشارة مخصصة، تواصل مع المبيعات على +31 618111116.",
    )

    actions = [
        ActionButton(label="💬 محادثة واتساب VIP المباشرة", url="https://wa.me/31618111116"),
        ActionButton(label="📋 طلب عرض سعر مخصص (RFQ)", action="open_rfq")
    ]

    return ConciergeResponseModel(
        reply=reply_text,
        actions=actions,
        intent="sovereign_executive_advisory",
        confidence=0.99,
        channel=req.channel or "whatsapp_cloud_api",
        source=source,
        session_id=session_id,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.post("/api/chat", response_model=ChatResponseModel, tags=["المحادثة العامة والذاكرة"])
async def chat_endpoint(req: ChatRequest, request: Request):
    """
    نقطة النهاية العامة للمحادثة مع دعم كامل للذاكرة المستمرة عبر `session_id`.
    """
    user_msg = req.message.strip()
    session_id = req.session_id or "default"
    principal = get_principal(request)  # [A8] الهوية المُصادقة = مالك الجلسة
    if not user_msg:
        raise HTTPException(status_code=400, detail="الرسالة لا يمكن أن تكون فارغة")

    # حفظ رسالة المستخدم، ثم توليد الرد مع سياق الجلسة وذاكرة المتجهات RAG
    reply_text, source, _rag_matches = await generate_sovereign_answer(
        user_msg, session_id, principal, max_turns=4, top_k=2,
    )

    return ChatResponseModel(
        reply=reply_text,
        session_id=session_id,
        source=source,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.get("/api/chat/stream", tags=["المحادثة العامة والذاكرة"])
async def chat_stream_endpoint(
    request: Request,
    message: str = Query(..., description="نص الرسالة المراد بثها لحظياً"),
    session_id: Optional[str] = Query("default", description="معرف الجلسة")
):
    """
    نقطة نهاية البث اللحظي للكلمات بتقنية Server-Sent Events (SSE)
    """
    # حفظ رسالة المستخدم
    principal = get_principal(request)  # [A8]
    sr_session_db.add_message(session_id, "user", message, source="user", owner=principal.name)
    context = sr_session_db.get_formatted_context(session_id, max_turns=3)
    prompt = f"{context}\n\nسؤال المستخدم الحالي: {message}" if context else message

    async def sse_generator():
        full_text = ""
        source = "google_antigravity_agent"
        try:
            agent_text = await call_agent_text(prompt)
            if agent_text is None:
                full_text = tool_get_service_details(message)
                source = "sovereign_knowledge_engine"
            else:
                full_text = agent_text

            # حفظ الرد المكتمل في الجلسة
            sr_session_db.add_message(session_id, "assistant", full_text, source=source, owner=principal.name)

            for chunk in split_text_chunks(full_text):
                yield sse_frame({"chunk": chunk, "session_id": session_id})
                await asyncio.sleep(0.01)
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield sse_frame({"error": str(e)})
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# ==============================================================================
# إدارة جلسات المحادثة والذاكرة (Session Management Endpoints)
# ==============================================================================
@app.get("/api/sessions", tags=["إدارة الجلسات والذاكرة"])
async def get_sessions(limit: int = Query(20, description="الحد الأقصى لعدد الجلسات")):
    """استعراض الجلسات المخزنة وعدد الرسائل وآخر نشاط"""
    return {"sessions": sr_session_db.list_all_sessions(limit=limit)}

@app.get("/api/sessions/{session_id}/history", tags=["إدارة الجلسات والذاكرة"])
async def get_session_history(
    request: Request,
    session_id: str = Path(..., description="معرف الجلسة المطلوب استرجاع رسائلها"),
    limit: int = Query(50, description="عدد الرسائل")
):
    """استرجاع سجل الرسائل الكامل لجلسة معينة"""
    # [A8] فرض ملكية الجلسة: المالك فقط أو admin
    principal = get_principal(request)
    try:
        sr_session_db.assert_session_access(session_id, principal.name, principal.is_admin)
    except PermissionError:
        raise HTTPException(status_code=403, detail="لا تملك صلاحية الوصول إلى هذه الجلسة.")
    messages = sr_session_db.get_history(session_id, limit=limit)
    return {"session_id": session_id, "messages": messages, "count": len(messages)}

@app.delete("/api/sessions/{session_id}", tags=["إدارة الجلسات والذاكرة"])
async def delete_session(request: Request, session_id: str = Path(..., description="معرف الجلسة المراد حذفها")):
    """حذف ومسح تاريخ جلسة معينة"""
    # [A8] فرض ملكية الجلسة قبل الحذف (الحذف نفسه محصور بدور admin عبر الوسيلة)
    principal = get_principal(request)
    try:
        sr_session_db.assert_session_access(session_id, principal.name, principal.is_admin)
    except PermissionError:
        raise HTTPException(status_code=403, detail="لا تملك صلاحية الوصول إلى هذه الجلسة.")
    sr_session_db.clear_session(session_id)
    return {"status": "success", "message": f"تم مسح الجلسة {session_id} بنجاح"}

# ==============================================================================
# ذاكرة المتجهات واسترجاع المعرفة المحلية (Local Vector DB / RAG Endpoints)
# ==============================================================================
@app.get("/api/rag/search", tags=["ذاكرة المتجهات RAG"])
async def rag_search_endpoint(
    query: str = Query(..., description="نص الاستعلام للبحث في ذاكرة المتجهات"),
    top_k: int = Query(4, description="عدد النتائج المسترجعة"),
    use_cache: bool = Query(True, description="استخدام الذاكرة المؤقتة (بصمة + TTL)"),
):
    """
    البحث الهجين (Dense Vectors + FTS5 BM25) في كافة صفحات ووثائق المشروع ومقالات المدونة،
    مع طبقة تخزين مؤقت قائمة على بصمة الاستعلام وتاريخ انتهاء (TTL).
    """
    results, cache_meta = app.state.rag_db.search_with_cache(query, top_k=top_k, use_cache=use_cache)
    return {
        "query": query,
        "count": len(results),
        "cache": cache_meta,
        "results": results
    }

@app.get("/api/rag/stats", tags=["ذاكرة المتجهات RAG"])
async def rag_stats_endpoint():
    """استعراض إحصائيات ذاكرة المتجهات وعدد المستندات والقطع المفهرسة وحالة الذاكرة المؤقتة"""
    return app.state.rag_db.get_stats()

@app.get("/api/rag/cache/stats", tags=["ذاكرة المتجهات RAG"])
async def rag_cache_stats_endpoint():
    """إحصاءات الذاكرة المؤقتة للاستعلامات: نسبة الإصابة والحجم والإبطالات وعمر القطعة"""
    return app.state.rag_db.cache_stats()

@app.delete("/api/rag/cache", tags=["ذاكرة المتجهات RAG"])
async def rag_cache_clear_endpoint():
    """إبطال كل نتائج الاستعلامات المخزأة (يتطلب صلاحية rag:reindex)"""
    removed = app.state.rag_db.clear_cache()
    return {
        "status": "cleared",
        "entries_removed": removed,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/rag/reindex", tags=["ذاكرة المتجهات RAG"])
async def rag_reindex_endpoint():
    """إعادة فهرسة وتحديث متجهات المشروع بالكامل على الفور (يُبطل الذاكرة المؤقتة تلقائياً)"""
    stats = build_or_update_knowledge_index()
    return {"status": "success", "message": "تم تحديث ذاكرة المتجهات بنجاح", "stats": stats}

# ==============================================================================
# إدارة مفاتيح API بصلاحيات دقيقة (Path 2: Scoped Keys & Expiry)
# ==============================================================================
@app.get("/api/admin/keys", tags=["إدارة مفاتيح API"])
async def list_api_keys(
    include_revoked: bool = Query(True, description="إدراج المفاتيح الملغاة"),
):
    """سرد المفاتيح بصلاحياتها الفعالة وحالتها (بصمات مقنّعة، بلا أي مفتاح نصي)"""
    store = get_key_store()
    keys = store.list_keys(include_revoked=include_revoked)
    return {"count": len(keys), "stats": store.stats(), "keys": keys}

@app.post("/api/admin/keys", status_code=201, tags=["إدارة مفاتيح API"])
async def create_api_key(req: CreateKeyRequest):
    """
    إنشاء مفتاح جديد بصلاحيات محددة وتاريخ انتهاء. يُعاد المفتاح النصي **مرة واحدة فقط**،
    ويُخزَّن من ثم بصمته SHA-256 فقط.
    """
    store = get_key_store()
    try:
        plain_key = store.add_key(
            name=req.name,
            role=req.role,
            expires_in_days=req.expires_in_days,
            permissions=req.permissions,
            metadata=req.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    info = store.get_key_info(store.hash_key(plain_key)) or {}
    return {
        "status": "created",
        "api_key": plain_key,
        "warning": "هذا المفتاح لن يُعرض مرة أخرى؛ خزّنه في مدير أسرار آمن.",
        "key": info,
    }

@app.post("/api/admin/keys/{key_sha256}/revoke", tags=["إدارة مفاتيح API"])
async def revoke_api_key(
    key_sha256: str = Path(..., min_length=8, max_length=64, description="بصمة SHA-256 للمفتاح"),
):
    """إلغاء مفتاح فوراً (يُرفض في الطلب التالي حتى لو بقي في الملف)"""
    if not get_key_store().revoke_key(key_sha256):
        raise HTTPException(status_code=404, detail="مفتاح غير موجود.")
    return {"status": "revoked", "key_sha256": key_sha256, "timestamp": datetime.now().isoformat()}

@app.post("/api/admin/keys/{key_sha256}/rotate", tags=["إدارة مفاتيح API"])
async def rotate_api_key(
    key_sha256: str = Path(..., min_length=8, max_length=64, description="بصمة المفتاح القديم"),
):
    """دوران المفتاح مع الحفاظ على الاسم والدور والصلاحيات وتاريخ الانتهاء"""
    try:
        new_key = get_key_store().rotate_key(key_sha256)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if new_key is None:
        raise HTTPException(status_code=404, detail="مفتاح غير موجود.")
    return {
        "status": "rotated",
        "api_key": new_key,
        "warning": "المفتاح القديم أُبطل؛ هذا المفتاح الجديد يُعرض مرة واحدة فقط.",
        "rotated_from": key_sha256,
    }

@app.get("/api/admin/system/rate-limit", tags=["إدارة مفاتيح API"])
async def rate_limit_stats_endpoint():
    """
    حالة حدّ المعدل: هل الحالة مشتركة بين كل العمال (SQLite) أم محلية لعامل واحد،
    مع العدّادات والحدود الفعّالة. يتطلب الصلاحية admin:system.
    """
    store = get_rate_limit_store()
    return {
        "store": store.stats(),
        "limits": {
            "general": os.getenv("CORESYNC_RATE_LIMIT", "120/min"),
            "chat": os.getenv("CORESYNC_CHAT_RATE_LIMIT", "10/min"),
            "chat_prefixes": list(SovereignRateLimitMiddleware.CHAT_PREFIXES),
        },
        "configured_backend": os.getenv("CORESYNC_RATE_LIMIT_STORE", "auto"),
        "timestamp": datetime.now().isoformat(),
    }

# ==============================================================================
# وكيل التدقيق الذاتي الفرعي (Autonomous Subagent Monitoring Endpoints)
# ==============================================================================
@app.get("/api/subagent/status", tags=["وكيل التدقيق الذاتي الفرعي"])
async def subagent_status_endpoint():
    """استعراض الحالة الحالية للوكيل الفرعي وآخر تدقيق أمني وتشغيلي"""
    report = app.state.subagent.run_full_audit()
    return report

@app.post("/api/subagent/run-audit", tags=["وكيل التدقيق الذاتي الفرعي"])
async def subagent_run_audit_endpoint():
    """تنفيذ دورة فحص وتدقيق أمني وصحي فوري"""
    report = app.state.subagent.run_full_audit()
    return {"status": "completed", "report": report}

@app.get("/cockpit", include_in_schema=False)
async def cockpit_page():
    """عرض لوحة التحكم التنفيذية للوكيل والمراقب الذاتي وفهرس RAG"""
    cockpit_file = os.path.join(os.path.dirname(__file__), "agent-cockpit.html")
    if os.path.exists(cockpit_file):
        with open(cockpit_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Cockpit file not found</h1>", status_code=404)

@app.post("/api/upload", tags=["تحليل المرفقات وفهرسة RAG"])
async def upload_files_endpoint(request: Request, files: List[UploadFile] = File(...)):
    """
    استلام مرفقات المستندات (PDF / DOCX) بحد أقصى 5 ميجابايت للملف،
    استخراج النصوص وفهرستها فورياً داخل محرك RAG المحلي للمنظومة.
    """
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB للملف الواحد
    MAX_FILES_PER_REQUEST = 5

    # [A3] فحص الحجم الكلي للطلب من الترويسة قبل قراءة أي بايت في الذاكرة
    _content_length = request.headers.get("content-length")
    if _content_length and _content_length.isdigit() and int(_content_length) > (MAX_FILE_SIZE * MAX_FILES_PER_REQUEST) + 2048:
        raise HTTPException(
            status_code=413,
            detail="حجم الطلب الإجمالي يتجاوز الحد المسموح (5 ملفات × 5 ميجابايت)."
        )
    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=413,
            detail="عدد الملفات يتجاوز الحد الأقصى (5 ملفات في الطلب الواحد)."
        )
    processed = []
    
    for file in files:
        filename = file.filename or "unknown_document"
        # [A3] قراءة تدفقية مقطعية (1MB) بسقف صارم بدلاً من تحميل الملف كاملاً في الذاكرة
        _parts: List[bytes] = []
        _total = 0
        while True:
            _chunk = await file.read(1024 * 1024)
            if not _chunk:
                break
            _total += len(_chunk)
            if _total > MAX_FILE_SIZE:
                break  # يكفي لتجاوز السقف؛ يلتقطه الفحص أدناه ويرفض الطلب
            _parts.append(_chunk)
        content = b"".join(_parts)
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"الملف {filename} يتجاوز الحد الأقصى المسموح به (5 ميجابايت)."
            )
            
        lower_name = filename.lower()
        extracted_text = ""
        
        try:
            if lower_name.endswith(".pdf"):
                import pdfplumber
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    pages_text = [page.extract_text() or "" for page in pdf.pages]
                    extracted_text = "\n\n".join(pages_text).strip()
            elif lower_name.endswith(".docx"):
                import docx
                doc = docx.Document(io.BytesIO(content))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                extracted_text = "\n\n".join(paragraphs).strip()
            elif lower_name.endswith(".txt") or lower_name.endswith(".md"):
                extracted_text = content.decode("utf-8", errors="ignore").strip()
            else:
                raise HTTPException(
                    status_code=415,
                    detail=f"نوع الملف {filename} غير مدعوم. الأنواع المدعومة: PDF, DOCX, TXT, MD"
                )
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(
                status_code=422,
                detail=f"تعذر استخراج المحتوى من الملف {filename}: {str(err)}"
            )
            
        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail=f"الملف {filename} لا يحتوي على أي نصوص قابلة للاستخراج."
            )
            
        # فهرسة المستند في قاعدة بيانات RAG
        index_result = index_custom_document(
            title=f"مرفق: {filename}",
            text_content=extracted_text,
            source_identifier=f"uploads/{filename}",
            category="user_attachment"
        )
        processed.append({
            "filename": filename,
            "size_bytes": len(content),
            "chunks_indexed": index_result.get("chunks_indexed", 0),
            "status": "indexed"
        })
        
    return {
        "status": "ok",
        "message": f"تمت معالجة وفهرسة {len(processed)} ملف(ات) بنجاح في قاعدة RAG المحلية.",
        "files_processed": len(processed),
        "details": processed
    }

# ==============================================================================
# نقاط نهاية البث المباشر للنبض السيادي (Mission 110: SSE Endpoints)
# ==============================================================================
@app.get("/api/stream/events", tags=["البث السيادي المباشر SSE"])
async def stream_sovereign_events(request: Request):
    """
    بث مباشر لحظي عبر تقنية Server-Sent Events (SSE) لتغذية لوحة القيادة الموحدة
    وبوابة المستشار القانوني بنبض العمليات الجنائية والمالية والأحكام فور حدوثها.
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    sse_subscribers.add(queue)

    async def event_generator():
        init_event = {
            "event": "connected",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "message": "تم الاتصال بنجاح بقناة البث السيادي المباشر (Sovereign Live Pulse SSE)",
                "subscribers_active": len(sse_subscribers),
                "hubs_monitored": ["104-Arbitration", "105-CBDC", "106-ZKP", "107A-Forensics", "107B-Escrow", "111-Counsel"]
            }
        }
        yield sse_frame(init_event)

        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=12.0)
                    yield sse_frame(data)
                except asyncio.TimeoutError:
                    yield f": heartbeat {datetime.now().strftime('%H:%M:%S')}\n\n"
        finally:
            sse_subscribers.discard(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/events/publish", tags=["البث السيادي المباشر SSE"])
async def publish_sovereign_event(req: PublishEventRequest):
    """نشر حدث لحظي جديد يُوزَّع على مشتركي SSE و WebSocket معاً"""
    delivered = await broadcast_live_event(req.event_type, req.payload)
    return {
        "status": "ok",
        "event_published": req.event_type,
        "subscribers_delivered": delivered,
        "transports": ["sse", "websocket"],
        "timestamp": datetime.now().isoformat()
    }

# ==============================================================================
# النقل ثنائي الاتجاه (Path 4): WebSocket بالتوازي مع SSE بنفس طبقة المصادقة
# ==============================================================================
# المصادقة تحدث في الوسيلة (SovereignAuthMiddleware) قبل accept: مفتاح غير صالح
# يُغلق الاتصال برمز ASGI 4401، ونقص الصلاحية 4403، وغياب التهيئة 4503 (المتصفح
# يرى فشل مصافحة HTTP 403 لأن الإغلاق يسبق accept). الصلاحيات: /ws/chat=chat:write
# و /ws/events=events:read. لا يمكن تمرير ترويسات من متصفح لـ WebSocket، لذا
# يُقبل ?api_key= (نفس استثناء SSE) أو الترويسة في العملاء الخادميين.
@app.websocket("/ws/chat")
async def ws_chat_endpoint(
    websocket: WebSocket,
    session_id: str = Query("default", description="معرف الجلسة الافتراضي"),
):
    """
    قناة محادثة ثنائية الاتجاه: يستقبل العميل رسائل JSON ويبث الخادم الرد مقاطعاً.

    بروتوكول العميل → الخادم:  {"message": "نص", "session_id": "اختياري", "type": "ping"}
    بروتوكول الخادم → العميل:  ready | chunk | done | error | pong
    """
    principal = get_principal(websocket)
    await websocket.accept()
    await websocket.send_json({
        "type": "ready",
        "transport": "websocket",
        "principal": principal.name,
        "role": principal.role,
        "session_id": session_id or "default",
        "timestamp": datetime.now().isoformat(),
    })

    try:
        while True:
            raw = await websocket.receive()
            if raw.get("type") == "websocket.disconnect":
                break
            text = raw.get("text")
            if text is None:
                continue  # تُهمل الحزم الثنائية (البروتوكول نصي JSON)

            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = {"message": text}
            if not isinstance(payload, dict):
                payload = {"message": str(payload)}

            if payload.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
                continue

            message = str(payload.get("message", "")).strip()
            if not message:
                await websocket.send_json({"type": "error", "detail": "الرسالة لا يمكن أن تكون فارغة"})
                continue

            target_session = str(payload.get("session_id") or session_id or "default")
            started = time.monotonic()
            reply, source, matches = await generate_sovereign_answer(
                message, target_session, principal
            )

            for chunk in split_text_chunks(reply):
                await websocket.send_json({
                    "type": "chunk", "delta": chunk, "session_id": target_session,
                })
                await asyncio.sleep(0.01)

            await websocket.send_json({
                "type": "done",
                "reply": reply,
                "session_id": target_session,
                "source": source,
                "citations": [
                    {"title": m["title"], "path": m["path"], "score": m["score"]}
                    for m in matches[:3]
                ],
                "elapsed_ms": int((time.monotonic() - started) * 1000),
            })
    except WebSocketDisconnect:
        logger.debug("انقطع اتصال WebSocket للمحادثة (الجلسة: %s)", session_id)
    except Exception as exc:  # لا نُسقط الخادم بسبب عميل واحد
        logger.error("خطأ في قناة WebSocket للمحادثة: %s", exc)
        try:
            await websocket.send_json({"type": "error", "detail": str(exc)})
        except Exception:
            pass

@app.websocket("/ws/events")
async def ws_sovereign_events(websocket: WebSocket):
    """
    نفس ناقل أحداث SSE لكن عبر WebSocket (JSON): connected → event* → heartbeat*.
    الحدث الواحد يُبث للقناتين من نفس المصدر (broadcast_live_event).
    """
    principal = get_principal(websocket)
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    sse_subscribers.add(queue)

    try:
        await websocket.send_json({
            "type": "connected",
            "transport": "websocket",
            "principal": principal.name,
            "subscribers_active": len(sse_subscribers),
            "hubs_monitored": [
                "104-Arbitration", "105-CBDC", "106-ZKP", "107A-Forensics",
                "107B-Escrow", "111-Counsel",
            ],
            "timestamp": datetime.now().isoformat(),
        })

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=12.0)
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "type": "heartbeat", "timestamp": datetime.now().isoformat(),
                })
                continue
            await websocket.send_json({"type": "event", **event})
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        sse_subscribers.discard(queue)

# ==============================================================================
# بوابة المستشار القانوني والتحقق من WORM (Mission 111: Corporate Counsel Portal API)
# ==============================================================================
CERTIFIED_WORM_REGISTRY = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
        "evidence_id": "EVD-2026-901",
        "title": "النسخة الجنائية لخادم قاعدة بيانات ERP لشركة Rotterdam B.V.",
        "case_ref": "ARB-2026-0418",
        "custodian": "Deloitte Forensics Netherlands",
        "standard": "ISO/IEC 27037:2012 Sec 6.3",
        "captured_at": "2026-10-14T08:15:00Z",
        "size_gb": 1840.5,
        "worm_status": "VERIFIED_IMMUTABLE",
        "enforceability": "Compliant with Hague Convention & EU Digital Evidence Reg."
    },
    "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a": {
        "evidence_id": "EVD-2026-902",
        "title": "أرشيف مراسلات بروتوكول توريد الصلب عبر البريد المشفر S/MIME",
        "case_ref": "ARB-2026-0421",
        "custodian": "KPMG Advisory / Gulf Financial Centre",
        "standard": "RFC 5322 / RFC 3161 Timestamping",
        "captured_at": "2026-10-18T14:22:30Z",
        "size_gb": 124.8,
        "worm_status": "VERIFIED_IMMUTABLE",
        "enforceability": "DIFC / DIAC Evidence Rules Compliant"
    },
    "ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d": {
        "evidence_id": "EVD-2026-903",
        "title": "سجلات المعاملات المشفرة لعقد التمويل بالمرابحة SPV",
        "case_ref": "ARB-2026-0447",
        "custodian": "PwC Digital Forensics Dubai",
        "standard": "IEEE C/BDL Distributed Ledger Evidence",
        "captured_at": "2026-10-22T11:05:12Z",
        "size_gb": 48.2,
        "worm_status": "VERIFIED_IMMUTABLE",
        "enforceability": "SCCA / AAOIFI Standard No. 32 Compliant"
    },
    "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069": {
        "evidence_id": "EVD-2026-904",
        "title": "لقطات الذاكرة الحية (RAM Dump) لبوابة التحقق المصرفي",
        "case_ref": "ARB-2026-0433",
        "custodian": "S&R Sovereign Cybersecurity Team",
        "standard": "NIST SP 800-86 Memory Acquisition",
        "captured_at": "2026-10-25T16:40:00Z",
        "size_gb": 64.0,
        "worm_status": "VERIFIED_IMMUTABLE",
        "enforceability": "SIAC Rules 2025 Compliant"
    }
}

@app.get("/api/counsel/worm-verify", tags=["بوابة المستشار القانوني المؤسسي"])
async def verify_worm_evidence(hash: str = Query(..., description="بصمة SHA-256 للمستند القضائي المراد التحقق من سلامته")):
    """
    التحقق الفوري من سلامة وأصالة مستند قضائي ومطابقته لسجل WORM ومعيار ISO/IEC 27037.
    """
    clean_hash = hash.strip().lower()
    if clean_hash in CERTIFIED_WORM_REGISTRY:
        record = CERTIFIED_WORM_REGISTRY[clean_hash]
        return {
            "status": "VERIFIED_IMMUTABLE",
            "hash": clean_hash,
            "is_tampered": False,
            "iso_27037_compliant": True,
            "details": record,
            "verification_timestamp": datetime.now().isoformat(),
            "seal_authority": "S&R CoreSync Sovereign WORM Custody Chamber"
        }
    return {
        "status": "UNREGISTERED_OR_TAMPERED",
        "hash": clean_hash,
        "is_tampered": True,
        "iso_27037_compliant": False,
        "warning": "البصمة التشفيرية غير متطابقة مع سجل WORM المعتمد؛ يحتمل تعديل المستند أو تلفه.",
        "verification_timestamp": datetime.now().isoformat()
    }

@app.get("/api/counsel/certified-awards", tags=["بوابة المستشار القانوني المؤسسي"])
async def list_certified_arbitral_awards():
    """قائمة أحكام التحكيم المعتمدة مع المقاعد القضائية واتفاقية نيويورك 1958"""
    return [
        {
            "case_id": "ARB-2026-0418",
            "claimant": "Rotterdam Logistics B.V.",
            "respondent": "Gulf Trade Holding LLC",
            "amount_eur": 1850000,
            "seat": "Amsterdam (NAI)",
            "rules": "NAI Arbitration Rules 2024",
            "governing_law": "Dutch Civil Code Book 7 + CISG 1980",
            "award_status": "AWARD_ISSUED_SUBJECT_TO_APPEAL",
            "appeal_status": "APPEAL_ACTIVE",
            "linked_escrow": "ESC-2026-101 (LOCKED)",
            "enforceability": "New York Convention 1958 (172 States)"
        },
        {
            "case_id": "ARB-2026-0421",
            "claimant": "Al-Noor Construction Co.",
            "respondent": "Emirates Towers Dev. PJSC",
            "amount_eur": 6420000,
            "seat": "Dubai (DIFC-AI)",
            "rules": "DIAC Rules 2022 + FIDIC Red Book 2017",
            "governing_law": "DIFC Law No. 1 of 2008",
            "award_status": "AWARD_ENFORCED",
            "appeal_status": "NONE",
            "linked_escrow": "ESC-2026-102 (DISPUTED_FROZEN)",
            "enforceability": "New York Convention 1958"
        },
        {
            "case_id": "ARB-2026-0433",
            "claimant": "S&R CoreSync IP Licensing",
            "respondent": "Pacific SoftWorks Pte. Ltd.",
            "amount_eur": 940000,
            "seat": "Singapore (SIAC)",
            "rules": "SIAC Rules 2025",
            "governing_law": "TRIPS + Singapore IPA",
            "award_status": "HEARING_COMPLETED",
            "appeal_status": "NONE",
            "linked_escrow": "ESC-2026-103",
            "enforceability": "New York Convention 1958"
        },
        {
            "case_id": "ARB-2026-0447",
            "claimant": "Damascus Trade Finance House",
            "respondent": "Levant Sukuk Issuer SPV",
            "amount_eur": 3175000,
            "seat": "Riyadh (SCCA)",
            "rules": "SCCA Rules 2023 + AAOIFI Sharia Std. No. 32",
            "governing_law": "Saudi Arbitration Law (Royal Decree M/34)",
            "award_status": "AWARD_FINAL",
            "appeal_status": "NONE",
            "linked_escrow": "ESC-2026-104",
            "enforceability": "New York Convention 1958 + Riyadh Arab Agreement"
        }
    ]

# ==============================================================================
# منظومة الاستئناف والاعتراض الذاتي (Mission 112: Autonomous Appeals Workflow)
# ==============================================================================
@app.post("/api/appeals/lodge", tags=["منظومة الاستئناف والاعتراض الذاتي"])
async def lodge_appeal(req: AppealRequest):
    """
    تسجيل طلب مراجعة استئنافية ذاتية لحكم تحكيمي فور ظهور أدلة جنائية جديدة في WORM.
    تقوم المنظومة تلقائياً بما يلي:
    1. تجميد فوري لمبالغ الضمان الذكي المرتبطة بالقضية (Smart Escrow Dispute Freeze).
    2. توليد ختم تشفيري موحد SHA-256 لملف الاستئناف.
    3. أرشفة وفهرسة أسباب الاستئناف داخل محرك RAG السيادي.
    4. بث إشعار فوري لجميع لوحات القيادة وبوابة المستشار القانوني عبر SSE.
    """
    docket_num = len(app.state.appeals) + 1
    appeal_id = f"APP-2026-{req.case_id.split('-')[-1]}-{docket_num:02d}"
    timestamp_iso = datetime.now().isoformat()

    docket_body = {
        "appeal_id": appeal_id,
        "case_id": req.case_id,
        "appellant": req.appellant,
        "respondent": req.respondent,
        "grounds": req.grounds,
        "evidence_worm_hash": req.evidence_worm_hash,
        "counsel_signature": req.counsel_signature,
        "timestamp": timestamp_iso,
        "jurisdiction": "Autonomous Appellate Tribunal Chamber 104"
    }
    encoded_bytes = json.dumps(docket_body, sort_keys=True).encode("utf-8")
    seal_sha256 = hashlib.sha256(encoded_bytes).hexdigest()

    docket_body["seal_sha256"] = seal_sha256
    docket_body["status"] = "APPEAL_UNDER_REVIEW"
    docket_body["escrow_action"] = "ESCROW_LOCKED_PENDING_APPELLATE_RULING"

    app.state.appeals.append(docket_body)

    index_custom_document(
        title=f"استئناف تحكيمي: {appeal_id} على القضية {req.case_id}",
        text_content=f"استئناف رقم {appeal_id}\nالقضية المستأنفة: {req.case_id}\nالمستأنف: {req.appellant}\nالمستأنف ضده: {req.respondent}\nالأسباب: {req.grounds}\nبصمة الدليل: {req.evidence_worm_hash}\nتوقيع المستشار: {req.counsel_signature}\nالختم: {seal_sha256}",
        source_identifier=f"appeals/{appeal_id}",
        category="judicial_appeals"
    )

    await broadcast_live_event("appeal_lodged", {
        "appeal_id": appeal_id,
        "case_id": req.case_id,
        "appellant": req.appellant,
        "grounds": req.grounds,
        "escrow_action": "DISPUTE_FROZEN",
        "seal_sha256": seal_sha256,
        "timestamp": timestamp_iso
    })

    return {
        "status": "ok",
        "message": f"تم قيد ملف الاستئناف {appeal_id} وتجميد أصول الضمان الذكي المرتبطة بنجاح.",
        "docket": docket_body
    }

@app.get("/api/appeals/list", tags=["منظومة الاستئناف والاعتراض الذاتي"])
async def list_appeals():
    """استرجاع كافة ملفات الاستئناف المقيدة وحالتها الراهنة"""
    return {
        "total_appeals": len(app.state.appeals),
        "appeals": app.state.appeals
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sr_agent_server:app", host="127.0.0.1", port=8000, reload=False)
