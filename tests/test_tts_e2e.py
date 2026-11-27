"""
=============================================================================
S&R CoreSync — اختبار طرفي (E2E) لمحرك TTS العصبي
=============================================================================
يغطي الأصوات الأربعة (ar/en × male/female) وحالات الرفض.

قواعد التشغيل:
  • افتراضياً **يُتخطّى** (لا يستهلك شبكة ولا يرفع سيرفراً) — لأنه يعتمد على
    مزوّد Edge Neural TTS الخارجي.
  • لتشغيله:            CORESYNC_TTS_E2E=1
  • لتشغيله يدوياً مع حفظ الملفات الصوتية في tests/tts_test_output:
        .venv\\Scripts\\python.exe tests\\test_tts_e2e.py

ملاحظة: النسخة السابقة كانت سكربتاً ينفّذ كل شيء وقت الاستيراد ويستدعي
sys.exit(1) عند تعذّر رفع السيرفر، فيُسقط جلسة pytest بأكملها عند تجميعه.
الآن كل شيء داخل اختبارات وفيكسترات، ولا يوجد أي sys.exit خارج __main__.
=============================================================================
"""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
SERVER_MODULE = "sr_agent_server:app"
OUTPUT_DIR = Path(__file__).resolve().parent / "tts_test_output"

# مفتاح اختباري محلي فقط: /api/tts يتطلب مصادقة (بلا صلاحية خاصة)، و/health عام
API_KEY = "sk-tts-e2e-local-only"
SERVER_ENV = {
    "CORESYNC_API_KEYS": f"tts-e2e:{API_KEY}:admin",
    "CORESYNC_AUTH_DISABLED": "0",
    "CORESYNC_RATE_LIMIT": "1000/min",
}

# تشغيل اختياري: بلا هذا المتغيّر لا يُلمس الشبكة إطلاقاً
RUN_E2E = os.environ.get("CORESYNC_TTS_E2E", "").strip().lower() in {"1", "true", "yes", "on"}

_REQUIRED_MODULES = ("fastapi", "uvicorn", "edge_tts")

# (label, text, lang, gender)
VOICE_CASES = [
    ("عربي_ذكر", "مرحباً بك في منصة إس آند آر كور سينك للحلول الذكية", "ar", "male"),
    ("عربي_أنثى", "مرحباً بك في منصة إس آند آر كور سينك للحلول الذكية", "ar", "female"),
    ("إنجليزي_ذكر", "Welcome to S and R CoreSync for Intelligent Solutions", "en", "male"),
    ("إنجليزي_أنثى", "Welcome to S and R CoreSync for Intelligent Solutions", "en", "female"),
]


def _skip_reason() -> str | None:
    if not (PROJECT / "sr_agent_server.py").is_file():
        return f"sr_agent_server.py غير موجود في {PROJECT}"
    missing = [m for m in _REQUIRED_MODULES if importlib.util.find_spec(m) is None]
    if missing:
        return "اعتماديات TTS غير مثبتة: " + ", ".join(missing) + " — ثبّتها أو تجاهل هذا الملف"
    if not RUN_E2E:
        return "اختبار E2E اختياري يعتمد على مزوّد خارجي — عيّن CORESYNC_TTS_E2E=1 لتشغيله"
    return None


_SKIP = _skip_reason()
pytestmark = pytest.mark.skipif(_SKIP is not None, reason=_SKIP or "")


# ── أدوات مساعدة ─────────────────────────────────────────────────────────────

def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _is_mp3(payload: bytes) -> bool:
    """ملف MP3 يبدأ بـ ID3 أو بإطار مزامنة 0xFFEx."""
    return payload[:3] == b"ID3" or (len(payload) > 1 and payload[0] == 0xFF and (payload[1] & 0xE0) == 0xE0)


def _server_env() -> dict:
    """بيئة نظيفة للسيرفر الفرعي: مفتاح معروف، وبلا ملف مفاتيح موروث."""
    env = {k: v for k, v in os.environ.items() if k not in {"CORESYNC_AUTH_FILE", "CORESYNC_AUTH_DISABLED"}}
    env.update(SERVER_ENV)
    return env


def _wait_ready(base: str, deadline_s: float = 90.0) -> None:
    """ينتظر جهوزية السيرفر عبر /health العام (لا يتأثر بالمصادقة)."""
    deadline = time.monotonic() + deadline_s
    last_error = "لا استجابة"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{base}/health", timeout=3) as resp:
                if resp.status == 200:
                    return
                last_error = f"HTTP {resp.status}"
        except Exception as exc:  # noqa: BLE001 — أي فشل يعني "ليس جاهزاً بعد"
            last_error = str(exc)
        time.sleep(0.5)
    raise TimeoutError(f"لم يستجب السيرفر خلال {deadline_s:.0f} ثانية (آخر خطأ: {last_error})")


def _post_tts(base: str, text: str, lang: str, gender: str, timeout: float = 60.0):
    """يرجع (status, content_type, body) — أو يرفع HTTPError كما هو."""
    payload = json.dumps({"text": text, "lang": lang, "gender": gender}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/tts",
        data=payload,
        headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.headers.get("content-type", ""), resp.read()


# ── فيكسترات ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def tts_base() -> str:
    """يرفع sr_agent_server على منفذ حر ويعيد عنوانه، ويُغلقه في النهاية."""
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    log_path = Path(tempfile.mkdtemp(prefix="coresync_tts_")) / "server.log"

    with open(log_path, "wb") as log:
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", SERVER_MODULE, "--host", "127.0.0.1",
             "--port", str(port), "--log-level", "warning"],
            cwd=str(PROJECT),
            env=_server_env(),
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        try:
            try:
                _wait_ready(base)
            except TimeoutError as exc:
                tail = log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
                pytest.fail(f"{exc}\nخروج العملية={server.poll()}\n--- سجل السيرفر ---\n{tail}")

            yield base
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


# ── الاختبارات ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("label,text,lang,gender", VOICE_CASES, ids=[c[0] for c in VOICE_CASES])
def test_tts_voice_returns_audio(tts_base, tmp_path, label, text, lang, gender):
    """كل تركيبة صوت تُرجع ملف MP3 سليماً بحجم معقول."""
    try:
        status, content_type, body = _post_tts(tts_base, text, lang, gender)
    except urllib.error.HTTPError as exc:
        if exc.code == 502:
            pytest.skip("مزوّد TTS الخارجي غير متاح حالياً (502) — ليس عطلاً في الكود")
        raise

    assert status == 200, f"{label}: رمز غير متوقع {status}"
    assert "audio" in content_type, f"{label}: نوع المحتوى {content_type!r} ليس صوتاً"
    assert len(body) > 1024, f"{label}: الصوت أصغر من المتوقع ({len(body)} بايت)"
    assert _is_mp3(body), f"{label}: الترويسة ليست MP3 صالحة ({body[:4]!r})"

    target = tmp_path / f"tts_{lang}_{gender}.mp3"
    target.write_bytes(body)
    assert target.stat().st_size == len(body)


def test_tts_empty_text_rejected(tts_base):
    """النص الفارغ يجب أن يُرفض بخطأ تحقق (422) لا أن يولّد صوتاً."""
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        _post_tts(tts_base, "", "ar", "male")
    assert excinfo.value.code == 422


def test_tts_unknown_lang_falls_back_to_arabic(tts_base):
    """لغة غير مدعومة تسقط إلى العربية بدل الفشل (سلوك مقصود في الخادم)."""
    try:
        status, content_type, body = _post_tts(tts_base, "اختبار السقوط إلى العربية", "fr", "male")
    except urllib.error.HTTPError as exc:
        if exc.code == 502:
            pytest.skip("مزوّد TTS الخارجي غير متاح حالياً (502)")
        raise
    assert status == 200 and "audio" in content_type and len(body) > 1024


# ── تشغيل يدوي كسكربت (اختياري) ─────────────────────────────────────────────

def _run_manually() -> int:
    """تشغيل يدوي يحفظ الملفات الصوتية في tests/tts_test_output."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    print(f"🚀 تشغيل السيرفر على {base} ...")

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", SERVER_MODULE, "--host", "127.0.0.1",
         "--port", str(port), "--log-level", "warning"],
        cwd=str(PROJECT),
        env=_server_env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    passed = 0
    try:
        try:
            _wait_ready(base)
            print("   ✅ السيرفر جاهز")
        except TimeoutError as exc:
            print(f"   ❌ {exc}")
            return 2

        for label, text, lang, gender in VOICE_CASES:
            try:
                _, content_type, body = _post_tts(base, text, lang, gender)
            except urllib.error.HTTPError as exc:
                print(f"   ❌ {label}: HTTP {exc.code}")
                continue
            ok = "audio" in content_type and _is_mp3(body)
            passed += ok
            path = OUTPUT_DIR / f"tts_{lang}_{gender}.mp3"
            path.write_bytes(body)
            print(f"   {'✅' if ok else '❌'} {label} — {len(body) / 1024:.1f} KB → {path}")
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()

    total = len(VOICE_CASES)
    print(f"\n📊 {passed}/{total} ناجح")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(_run_manually())
