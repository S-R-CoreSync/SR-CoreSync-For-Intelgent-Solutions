<div dir="rtl">

# 🔐 المصادقة الدقيقة، الذاكرة المؤقتة، و WebSocket — دليل الخادم 2.1

**الملفات:** `sr_auth_advanced.py` · `sr_auth.py` · `sr_rate_limit.py` · `sr_rag_engine.py` · `sr_agent_server.py`
**الاختبارات:** `tests/unit/test_sr_auth_advanced.py` · `tests/unit/test_rate_limit.py` · `tests/unit/test_rag_cache.py` · `tests/integration/test_realtime_and_scoped_keys.py`
**الحالة:** 195 اختباراً ناجحاً (42 سابقة + 153 جديدة) — 0 فشل.

---

## 1. الصلاحيات الدقيقة (Path 2)

### 1.1 شكل الصلاحية

كل صلاحية بصيغة `<المورد>:<الإجراء>`، والإجراء يبدأ من نطاقَي `read` / `write` ويعلو إلى `admin` (`list`، `delete`، `reindex`، `publish`، `run`، `keys`…) حسب حساسية العملية.

### 1.2 كتالوج الصلاحيات

| المورد | الصلاحيات |
|---|---|
| المحادثة | `chat:read` · `chat:write` |
| الجلسات | `sessions:read` · `sessions:write` · `sessions:list` · `sessions:delete` |
| ذاكرة المتجهات | `rag:read` · `rag:write` · `rag:reindex` |
| المرفقات | `upload:write` |
| البث المباشر | `events:read` · `events:publish` |
| البوابة القانونية | `appeals:read` · `appeals:write` |
| التدقيق الذاتي | `subagent:read` · `subagent:run` |
| الإدارة | `admin:keys` · `admin:system` |

### 1.3 الأدوار الافتراضية

| الدور | المنح | الاستخدام |
|---|---|---|
| `admin` | كل الصلاحيات (وأي صلاحية تُضاف مستقبلاً) | وحدة التحكم، الإدارة، إدارة المفاتيح |
| `writer` | قراءة + كتابة تشغيلية (بلا `rag:reindex` وبلا `admin:*`) | تكاملات الشركاء التي ترفع مستندات وتحادث |
| `client` | `chat:*` · `sessions:read/write` · `rag:read` · `events:read` | ويدجت الموقع وتطبيق العميل |
| `readonly` | `chat:read` · `sessions:read` · `rag:read` · `events:read` | لوحات المراقبة والتقارير |

> يمكن تجاوز صلاحيات الدور **لكل مفتاح على حدة** عبر `permissions` عند الإنشاء (مثال: مفتاح بدور `client` مقيّد بـ `rag:read` فقط).

### 1.4 خريطة المسارات → الصلاحيات

الخريطة مركزية في `sr_auth_advanced.ROUTE_PERMISSIONS` وتُطبَّق في وسيلة المصادقة على HTTP و WebSocket معاً:

| المسار | الصلاحية |
|---|---|
| `POST /api/chat` · `GET /api/chat/stream` · `POST /api/ai-concierge` | `chat:write` |
| `WS /ws/chat` | `chat:write` |
| `GET /api/sessions` | `sessions:list` |
| `GET /api/sessions/{id}/history` | `sessions:read` |
| `DELETE /api/sessions/{id}` | `sessions:delete` |
| `GET /api/rag/search` · `/api/rag/stats` · `/api/rag/cache/stats` | `rag:read` |
| `DELETE /api/rag/cache` · `POST /api/rag/reindex` | `rag:reindex` |
| `POST /api/upload` | `upload:write` |
| `GET /api/stream/events` · `WS /ws/events` | `events:read` |
| `POST /api/events/publish` | `events:publish` |
| `GET /api/counsel/*` · `GET /api/appeals/list` | `appeals:read` |
| `POST /api/appeals/lodge` | `appeals:write` |
| `GET /api/subagent/status` | `subagent:read` |
| `POST /api/subagent/run-audit` | `subagent:run` |
| `/api/admin/keys*` | `admin:keys` |

- المسارات غير المذكورة تتطلب **مفتاحاً صالحاً فقط** (كما قبل 2.1).
- الرفض يحمل سبباً قابلاً للقراءة آلياً: `{"status": "forbidden", "required_permission": "chat:write"}` برمز 403.

### 1.5 تاريخ الانتهاء والإلغاء

- `expires_at` يُفحص في **كل طلب**؛ المفتاح المنتهي يُرفض بـ 401 حتى لو بقي في الملف.
- تاريخ انتهاء تالف (غير قابل للتحليل) = مفتاح غير صالح (إغلاق افتراضي، لا عمر مفتوح).
- الإلغاء (`is_revoked`) نهائي وفوري، ويُسجَّل في الملف.

---

## 2. دورة حياة المفتاح عبر API

كل نقاط الإدارة تتطلب `admin:keys`، وتعيد بصمات مقنّعة فقط:

```powershell
$ADMIN = "sk_live_xxxxxxxx"   # مفتاح بدور admin
$BASE  = "http://127.0.0.1:8000"

# 1) إنشاء مفتاح مقيّد لمدة 30 يوماً
Invoke-RestMethod -Method Post "$BASE/api/admin/keys" -Headers @{ "X-API-Key" = $ADMIN } `
  -ContentType "application/json" -Body (@{
      name = "partner-portal-eu"; role = "writer"; expires_in_days = 30;
      metadata = @{ owner = "partners"; env = "prod" }
  } | ConvertTo-Json)

# 2) سرد المفاتيح وحالتها
Invoke-RestMethod "$BASE/api/admin/keys" -Headers @{ "X-API-Key" = $ADMIN }

# 3) إلغاء مفتاح (بالبصمة)
Invoke-RestMethod -Method Post "$BASE/api/admin/keys/<sha256>/revoke" -Headers @{ "X-API-Key" = $ADMIN }

# 4) دوران المفتاح (يحافظ على الاسم والدور والصلاحيات والانتهاء)
Invoke-RestMethod -Method Post "$BASE/api/admin/keys/<sha256>/rotate" -Headers @{ "X-API-Key" = $ADMIN }
```

**قواعد مهمة:**
- المفتاح النصي يُعاد **مرة واحدة فقط** لحظة الإنشاء/الدوران؛ لا يُخزَّن ولا يُسجَّل.
- التخزين بصمة `SHA-256` فقط، والكتابة إلى `auth_keys.json` **ذرّية** (`tmp` + `os.replace`) وبصلاحيات `0600` على POSIX.
- عدّادات الاستخدام تُجمَّع في الذاكرة وتُفرَّغ عند عملية إدارية أو عند إطفاء الخادم (لا كتابة قرص في مسار المصادقة).
- التكرار مرفوض: نفس المفتاح النصي لا يُنشأ مرتين (استخدم الدوران).
- الأدوار المتاحة: `admin` · `writer` · `client` · `readonly` (أي دور آخر → 400).

---

## 3. الذاكرة المؤقتة لاستعلامات RAG (Path 3)

### 3.1 لماذا

البحث الهجين يقرأ كل القطع من SQLite ويحسب تشابه المتجهات لكل قطعة في **كل** استدعاء. الأسئلة المتكررة (نفس الواجهة، نفس جلسة المحاكاة، نفس استفسار الدعم) تُعاد الآن دون إعادة الحساب، فتقلّ زمن الاستجابة والحمل قبل أي نداء لنموذج Gemini.

### 3.2 كيف تعمل

- **المفتاح (بصمة):** `SHA-256` من (اسم قاعدة البيانات + إصدار الفهرس + الاستعلام المُطبَّع عربياً/لاتينياً + `top_k` + `alpha`).
  التطبيع يجمع `إحكام` و`احكام` و`أحكام` على بصمة واحدة (نفس منطق `normalize_text`).
- **TTL:** 300 ثانية افتراضياً؛ بعدها تُحتسب القطعة منتهية وتُحذف عند أول قراءة.
- **LRU:** سقف 256 استعلاماً؛ عند التجاوز يُخلّى الأقدم استخداماً.
- **الإبطال:** أي كتابة في الفهرس (`upsert_document` عبر الرفع أو إعادة الفهرسة أو قيد استئناف) تُفرغ الذاكرة تلقائياً — لا يُخدم سياق قديم أبداً.
- **العزل:** كل قراءة تُعيد نسخة مستقلة (deepcopy)؛ لا يستطيع مستدعٍ إفساد النتائج المخزأة لغيره.
- **التزامن:** `threading.RLock` لأن FastAPI قد يخدم طلبات متوازية.

### 3.3 المتغيرات البيئية

| المتغير | الافتراضي | المعنى |
|---|---|---|
| `CORESYNC_RAG_CACHE_TTL` | `300` | عمر القطعة بالثواني (`0` = تعطيل الطبقة) |
| `CORESYNC_RAG_CACHE_MAX_ENTRIES` | `256` | سقف عدد الاستعلامات المخزأة (LRU) |

### 3.4 نقاط النهاية

| المسار | الصلاحية | الوظيفة |
|---|---|---|
| `GET /api/rag/search?query=...&top_k=4&use_cache=true` | `rag:read` | بحث هجين + حقل `cache` يوضح `hit` / `miss` / `bypass` |
| `GET /api/rag/cache/stats` | `rag:read` | `hits`, `misses`, `hit_rate`, `size`, `expirations`, `lru_evictions`… |
| `DELETE /api/rag/cache` | `rag:reindex` | إبطال كل النتائج وإرجاع عدد المُزال |
| `GET /api/rag/stats` | `rag:read` | يتضمن الآن بلوك `query_cache` |

مثال استجابة:

```json
{
  "query": "التحكيم التجاري",
  "count": 2,
  "cache": { "status": "hit", "fingerprint": "9f2c1a7be4d0", "ttl_seconds": 300.0 },
  "results": [ ... ]
}
```

---

## 4. WebSocket بالتوازي مع SSE (Path 4)

### 4.1 المصادقة (قبل `accept`)

| الحالة | النتيجة |
|---|---|
| مفتاح مفقود / خاطئ / منتهٍ / ملغى | إغلاق **4401** |
| مفتاح صالح بلا الصلاحية المطلوبة | إغلاق **4403** |
| لا مفاتيح مهيّأة على الخادم | إغلاق **4503** |

الوسيلة ترفض الاتصال **قبل** `accept`، فلا يُفتح أي اتصال غير مُصرَّح به. يُقبل المفتاح من `?api_key=` (لأن المتصفح لا يسمح بترويسات مخصّصة في WebSocket) أو من الترويسة `X-API-Key` في العملاء الخادميين.

> **ملاحظة على ما يراه العميل:** لأن الرفض يحدث قبل `accept`، يرى المتصفح **فشل مصافحة** (HTTP 403) دون رمز تطبيقي؛ أما الرموز 4401/4403/4503 فهي إطار الإغلاق على مستوى ASGI وتظهر في الاختبارات والسجلات وأي عميل يقرأ إطار الإغلاق.

### 4.2 `/ws/chat` — محادثة ثنائية الاتجاه

**العميل → الخادم**

```json
{"message": "ما هي باقاتكم؟", "session_id": "client_101"}
{"type": "ping"}
```

**الخادم → العميل**

```json
{"type": "ready", "transport": "websocket", "principal": "site-widget", "role": "client", "session_id": "client_101"}
{"type": "chunk", "delta": "بناءً على ", "session_id": "client_101"}
{"type": "done", "reply": "...", "session_id": "client_101", "source": "sovereign_rag_knowledge_engine",
 "citations": [{"title": "…", "path": "index.html", "score": 0.71}], "elapsed_ms": 42}
{"type": "error", "detail": "الرسالة لا يمكن أن تكون فارغة"}
{"type": "pong", "timestamp": "2026-11-25T17:04:11"}
```

**مثال متصفح:**

```js
const ws = new WebSocket(`wss://sr-coresync.com/ws/chat?api_key=${KEY}&session_id=client_101`);
ws.onmessage = (e) => {
  const frame = JSON.parse(e.data);
  if (frame.type === "chunk") process.stdout?.write?.(frame.delta) ?? (window.__buf += frame.delta);
  if (frame.type === "done") console.log("اكتمل:", frame.reply, frame.citations);
};
ws.onopen = () => ws.send(JSON.stringify({ message: "ما هي باقاتكم؟" }));
```

**مثال Python:**

```python
import asyncio, json, websockets

async def ask():
    uri = "ws://127.0.0.1:8000/ws/chat?api_key=sk_live_xxx&session_id=py-1"
    async with websockets.connect(uri) as ws:
        print(json.loads(await ws.recv())["type"])          # ready
        await ws.send(json.dumps({"message": "التحكيم التجاري"}))
        while True:
            frame = json.loads(await ws.recv())
            if frame["type"] == "chunk":
                print(frame["delta"], end="", flush=True)
            elif frame["type"] == "done":
                break

asyncio.run(ask())
```

- كل رسالة تُحفظ في نفس قاعدة جلسات HTTP (`session_id` مشترك) — يمكن متابعة الحوار بين القناتين.
- يمرّ الرد بنفس خط التوليد: سياق الجلسة + RAG المخزأ مؤقتاً + وكيل Antigravity أو الصمود السيادي.

### 4.3 `/ws/events` — ناقل الأحداث السيادية

```json
{"type": "connected", "transport": "websocket", "subscribers_active": 3, "hubs_monitored": ["104-Arbitration", "..."]}
{"type": "event", "event": "appeal_lodged", "timestamp": "2026-11-25T17:05:00", "payload": {...}}
{"type": "heartbeat", "timestamp": "2026-11-25T17:05:12"}
```

- نفس مجموعة المشتركين التي تغذي SSE: `POST /api/events/publish` (أو أي حدث داخلي مثل `appeal_lodged`) يصل إلى **القناتين** بنفس المخطط.
- SSE القديم لم يتغيّر سلوكياً: نفس `data: {...}` و`: heartbeat` كل 12 ثانية.

---

## 5. اختبارات

```powershell
# المجموعة الكاملة (195 اختباراً)
.\.venv\Scripts\python.exe -m pytest tests -q

# حدّ المعدل المشترك (نافذة منزلقة، تعدد العمال)
.\.venv\Scripts\python.exe -m pytest tests/unit/test_rate_limit.py -q

# الوحدوية الجديدة
.\.venv\Scripts\python.exe -m pytest tests/unit/test_sr_auth_advanced.py tests/unit/test_rag_cache.py -q

# التكامل (WebSocket + الذاكرة المؤقتة + إدارة المفاتيح)
.\.venv\Scripts\python.exe -m pytest tests/integration/test_realtime_and_scoped_keys.py -q
```

`tests/conftest.py` يعزل `CORESYNC_AUTH_FILE` في مجلد مؤقت، فلا تُلمس `auth_keys.json` الحقيقية أثناء الاختبارات (مُتحقَّق منه بالبصمة).

---

## 6. حدّ المعدل المشترك بين العمليات (`sr_rate_limit.py`)

### 6.1 المشكلة التي أُغلقت

كان العدّاد `dict` داخل ذاكرة كل عملية. النتيجة: مع `uvicorn --workers 4` يصبح الحدّ الفعلي **4 × الحد**، ويُصفَّر كل عدّاد عند إعادة التشغيل. الحلّ ليس Redis مدفوعاً، بل حالة مشتركة على القرص.

### 6.2 الحل الافتراضي: نافذة منزلقة في SQLite

- ملف واحد (`sr_rate_limit.db`) يشاركه كل العمال والعمليات على المضيف، بـ `WAL` و`busy_timeout`.
- `BEGIN IMMEDIATE` يجعل “اعدد ثم أدرج” عملية ذرّية واحدة، فلا سباق بين العمال.
- **نافذة منزلقة حقيقية** (لا نافذة ثابتة): الطلب يُرفض إذا بلغ عدد الطلبات المقبولة داخل آخر `window` ثانية الحدَّ، ويُعاد `retry_after` حتى يتحرر أقدم طلب. النافذة الثابتة كانت ستسمح بانفجار مضاعف عند حدود النوافذ.
- تنظيف دوري للصفوف الخارجة عن الأفق (ساعتان)، مع حماية من قفزات الساعة للخلف.

### 6.3 الخلفيات والتدرّج الآمن

| `CORESYNC_RATE_LIMIT_STORE` | السلوك |
|---|---|
| `auto` (افتراضي) | SQLite إن أمكن الكتابة، وإلا الذاكرة مع تحذير |
| `sqlite` | SQLite صراحةً، مع تراجع إلى الذاكرة عند فشل التهيئة |
| `memory` | الذاكرة فقط (تطوير/اختبارات) |

**سياسة الفشل:** الانفتاح مع تسجيل (Fail-Open). حدّ المعدل حماية إساءة استخدام لا وسيلة مصادقة؛ انقطاع القرص لا يجوز أن يُسقط الخدمة، وتُسجَّل الحادثة بـ `warning`.

### 6.4 الإعداد والفحص

| المتغير | الافتراضي | المعنى |
|---|---|---|
| `CORESYNC_RATE_LIMIT` | `120/min` | الحد العام لكل هوية/عنوان |
| `CORESYNC_CHAT_RATE_LIMIT` | `10/min` | حد مسارات المحادثة المكلفة |
| `CORESYNC_RATE_LIMIT_STORE` | `auto` | `auto` / `sqlite` / `memory` |
| `CORESYNC_RATE_LIMIT_DB` | `sr_rate_limit.db` | مسار ملف العدّادات |

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/admin/system/rate-limit" -Headers @{ "X-API-Key" = $ADMIN }
```

```json
{
  "store": { "backend": "sqlite", "shared_across_workers": true, "tracked_hits": 37,
             "active_identities": 4, "accepted_total": 37, "rejected_total": 2 },
  "limits": { "general": "120/min", "chat": "10/min" }
}
```

يتطلب `admin:system`؛ والمفتاح `shared_across_workers` هو ما يخبرك فوراً: هل الحالة مشتركة فعلاً أم تراجعت إلى الذاكرة؟

### 6.5 الحدود المعروفة

- **نفس المضيف:** مشترك بالفعل — لا إعداد إضافي.
- **عدة مضيفات:** الملف المحلي لا يُشارك عبر الأجهزة؛ ضع موازناً/Nginx في المقدمة أو مخزناً مركزياً. ملاحظة مهمة: `nginx.conf` في هذا المستودع يخدم **الملفات الثابتة فقط** ولا يمرّر `/api`، لذا إضافة `limit_req` له ستكون إعداداً ميتاً حتى يُضاف `proxy_pass` فعلي.
- **الأداء:** كل طلب محمي = معاملة صغيرة على ملف محلي (‏0.1–0.3ms)، والتنظيف يجري كل 500 عملية.

---

## 7. ملاحظات أمنية وتشغيلية

1. **الإغلاق الافتراضي:** بلا أي مفتاح، الخادم يرفض الطلبات المحمية بـ 503 (لا يعمل مفتوحاً). للتطوير المحلي فقط: `CORESYNC_AUTH_DISABLED=1`.
2. **لا أسرار في السجلات:** كل الرسائل تستخدم بصمة مقنّعة (`mask_digest`)، ولا يُسجَّل أي مفتاح نصي.
3. **حد المعدل مشترك افتراضياً:** الحالة في `sr_rate_limit.db` يشترك فيها كل عمال المضيف، فلا يتضاعف الحدّ. عند التوسع على **عدة مضيفات** ضع موازناً في المقدمة أو مخزناً مركزياً.
4. **حدود المصادقة في WebSocket:** المتصفح لا يمرر ترويسات، لذا يظهر المفتاح في سلسلة الاستعلام. استخدم `wss://` دائماً، وأبقِ عمر المفاتيح قصيراً (`expires_in_days`) للواجهات العامة.
5. **إبطال فوري:** إلغاء/دوران المفتاح يسري على الطلب التالي بلا إعادة تشغيل (المخزن مشترك في العملية الواحدة).
6. **تعدد العمال:** كل عملية تحمل نسختها من `auth_keys.json`؛ بعد إدارة المفاتيح أعد التحميل (إعادة تشغيل) أو انتقل لمخزن مركزي عند تشغيل أكثر من عامل.

</div>
