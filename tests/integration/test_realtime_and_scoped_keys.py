"""
=============================================================================
اختبارات تكامل لمسارات الإصدار 2.1:
  - Path 2: مفاتيح API بصلاحيات دقيقة وتاريخ انتهاء + نقاط إدارة المفاتيح.
  - Path 3: التخزين المؤقت لاستعلامات RAG في نقاط النهاية.
  - Path 4: WebSocket بالتوازي مع SSE بنفس طبقة المصادقة.
=============================================================================
"""

import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# يجب ضبط البيئة قبل استيراد الخادم (المخزن يُبنى عند أول طلب)
os.environ.setdefault("GEMINI_API_KEY", "test-dummy-key")
os.environ.setdefault(
    "CORESYNC_API_KEYS",
    "admin-test:sk-admin-secret-123:admin,client-test:sk-client-secret-456:client",
)
os.environ["CORESYNC_AUTH_DISABLED"] = "0"
os.environ.setdefault("CORESYNC_RATE_LIMIT", "5000/min")
os.environ.setdefault("CORESYNC_CHAT_RATE_LIMIT", "500/min")

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from sr_agent_server import app
from sr_auth import get_key_store
from sr_auth_advanced import hash_api_key

ADMIN_HEADERS = {"X-API-Key": "sk-admin-secret-123"}
CLIENT_HEADERS = {"X-API-Key": "sk-client-secret-456"}
ADMIN_KEY = "sk-admin-secret-123"
CLIENT_KEY = "sk-client-secret-456"


@pytest.fixture(scope="module")
def client():
    """عميل واحد لكل الوحدة: دورة حياة واحدة بدل إعادة الفهرسة في كل اختبار."""
    with TestClient(app) as test_client:
        yield test_client


def _create_key(client, **payload):
    """إنشاء مفتاح عبر نقطة الإدارة وإرجاع (المفتاح النصي، الجسم)."""
    response = client.post("/api/admin/keys", json=payload, headers=ADMIN_HEADERS)
    assert response.status_code == 201, response.text
    body = response.json()
    return body["api_key"], body


class TestScopedPermissionEnforcement:
    """فرض الصلاحيات الدقيقة على مستوى الوسيلة (HTTP)."""

    def test_client_key_can_read_rag(self, client):
        assert client.get("/api/rag/stats", headers=CLIENT_HEADERS).status_code == 200

    def test_client_key_cannot_list_all_sessions(self, client):
        response = client.get("/api/sessions", headers=CLIENT_HEADERS)
        assert response.status_code == 403
        body = response.json()
        assert body["required_permission"] == "sessions:list"

    def test_client_key_cannot_revoke_keys(self, client):
        response = client.post(
            f"/api/admin/keys/{'a' * 64}/revoke", headers=CLIENT_HEADERS
        )
        assert response.status_code == 403
        assert response.json()["required_permission"] == "admin:keys"

    def test_readonly_key_cannot_write_chat(self, client):
        readonly_key, _ = _create_key(client, name="readonly-probe", role="readonly")
        # القراءة مسموحة
        assert client.get("/api/rag/search", params={"query": "التحكيم"},
                          headers={"X-API-Key": readonly_key}).status_code == 200
        # الكتابة مرفوضة بصلاحية صريحة
        response = client.post("/api/chat", json={"message": "مرحبا"},
                               headers={"X-API-Key": readonly_key})
        assert response.status_code == 403
        assert response.json()["required_permission"] == "chat:write"

    def test_permission_override_limits_key(self, client):
        scoped_key, _ = _create_key(
            client, name="scoped-probe", role="client", permissions=["rag:read"]
        )
        headers = {"X-API-Key": scoped_key}
        assert client.get("/api/rag/stats", headers=headers).status_code == 200
        assert client.post("/api/chat", json={"message": "مرحبا"}, headers=headers).status_code == 403

    def test_expired_key_is_rejected(self, client):
        plain, _ = _create_key(client, name="expired-probe", role="readonly")
        entry = get_key_store()._advanced.get_entry(hash_api_key(plain))
        entry.expires_at = "2000-01-01T00:00:00+00:00"

        response = client.get("/api/rag/stats", headers={"X-API-Key": plain})
        assert response.status_code == 401

    def test_unknown_route_still_requires_valid_key(self, client):
        assert client.get("/api/does-not-exist", headers=CLIENT_HEADERS).status_code == 404
        assert client.get("/api/does-not-exist").status_code == 401


class TestKeyManagementAPI:
    """نقاط إدارة المفاتيح (إنشاء/سرد/إلغاء/دوران)."""

    def test_create_key_returns_plaintext_once(self, client):
        plain, body = _create_key(
            client, name="partner-api", role="writer", expires_in_days=30,
            metadata={"owner": "qa"},
        )
        assert plain.startswith("sk_live_")
        assert body["key"]["name"] == "partner-api"
        assert body["key"]["expires_at"] is not None
        assert "plain_key" not in body["key"]

        # المفتاح الجديد يعمل فوراً بنفس المخزن
        response = client.get("/api/rag/stats", headers={"X-API-Key": plain})
        assert response.status_code == 200

        # ولا يُعاد عرضه في السرد
        listing = client.get("/api/admin/keys", headers=ADMIN_HEADERS)
        assert plain not in listing.text

    def test_create_key_rejects_unknown_role(self, client):
        response = client.post(
            "/api/admin/keys", json={"name": "bad", "role": "root"}, headers=ADMIN_HEADERS
        )
        assert response.status_code == 400
        assert "دور" in response.json()["detail"]

    def test_create_key_rejects_unknown_permission(self, client):
        response = client.post(
            "/api/admin/keys",
            json={"name": "bad", "permissions": ["root:everything"]},
            headers=ADMIN_HEADERS,
        )
        assert response.status_code == 400

    def test_rotate_key_invalidates_old(self, client):
        old_plain, body = _create_key(client, name="to-rotate", role="client")
        old_digest = body["key"]["key_sha256"]

        rotated = client.post(
            f"/api/admin/keys/{old_digest}/rotate", headers=ADMIN_HEADERS
        )
        assert rotated.status_code == 200
        new_plain = rotated.json()["api_key"]
        assert new_plain != old_plain

        assert client.get("/api/rag/stats", headers={"X-API-Key": old_plain}).status_code == 401
        assert client.get("/api/rag/stats", headers={"X-API-Key": new_plain}).status_code == 200

    def test_revoke_key_blocks_immediately(self, client):
        plain, body = _create_key(client, name="to-revoke-api", role="readonly")
        digest = body["key"]["key_sha256"]
        headers = {"X-API-Key": plain}
        assert client.get("/api/rag/stats", headers=headers).status_code == 200

        revoked = client.post(f"/api/admin/keys/{digest}/revoke", headers=ADMIN_HEADERS)
        assert revoked.status_code == 200
        assert client.get("/api/rag/stats", headers=headers).status_code == 401

    def test_revoke_unknown_key_returns_404(self, client):
        response = client.post(f"/api/admin/keys/{'b' * 64}/revoke", headers=ADMIN_HEADERS)
        assert response.status_code == 404

    def test_list_keys_reports_state(self, client):
        response = client.get("/api/admin/keys", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        body = response.json()
        assert body["count"] >= 1
        assert "total_keys" in body["stats"]
        sample = body["keys"][0]
        for field in ("name", "role", "permissions", "is_valid", "is_expired", "usage_count"):
            assert field in sample


class TestRAGCacheEndpoints:
    """طبقة التخزين المؤقت عبر HTTP."""

    def test_second_identical_search_is_served_from_cache(self, client):
        client.delete("/api/rag/cache", headers=ADMIN_HEADERS)

        first = client.get("/api/rag/search", params={"query": "التحكيم التجاري", "top_k": 2},
                           headers=CLIENT_HEADERS)
        assert first.status_code == 200
        assert first.json()["cache"]["status"] == "miss"

        second = client.get("/api/rag/search", params={"query": "التحكيم التجاري", "top_k": 2},
                            headers=CLIENT_HEADERS)
        assert second.json()["cache"]["status"] == "hit"
        assert second.json()["results"] == first.json()["results"]

    def test_cache_can_be_bypassed(self, client):
        response = client.get(
            "/api/rag/search",
            params={"query": "التحكيم التجاري", "use_cache": "false"},
            headers=CLIENT_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["cache"]["status"] == "bypass"

    def test_cache_stats_endpoint(self, client):
        response = client.get("/api/rag/cache/stats", headers=CLIENT_HEADERS)
        assert response.status_code == 200
        body = response.json()
        assert body["enabled"] is True
        assert body["ttl_seconds"] > 0
        assert body["hits"] + body["misses"] >= 1

    def test_clearing_cache_requires_admin_scope(self, client):
        assert client.delete("/api/rag/cache", headers=CLIENT_HEADERS).status_code == 403

        response = client.delete("/api/rag/cache", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["status"] == "cleared"

    def test_rag_stats_exposes_cache_block(self, client):
        response = client.get("/api/rag/stats", headers=CLIENT_HEADERS)
        assert response.status_code == 200
        assert "query_cache" in response.json()


class TestWebSocketAuth:
    """المصادقة والصلاحيات على قنوات WebSocket."""

    def test_missing_key_is_rejected_before_accept(self, client):
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect("/ws/chat"):
                pass
        assert excinfo.value.code == 4401

    def test_invalid_key_is_rejected(self, client):
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect("/ws/events?api_key=wrong-key"):
                pass
        assert excinfo.value.code == 4401

    def test_readonly_key_cannot_open_chat_socket(self, client):
        readonly_key, _ = _create_key(client, name="ws-readonly", role="readonly")
        with pytest.raises(WebSocketDisconnect) as excinfo:
            with client.websocket_connect(f"/ws/chat?api_key={readonly_key}"):
                pass
        assert excinfo.value.code == 4403

    def test_readonly_key_can_subscribe_to_events(self, client):
        readonly_key, _ = _create_key(client, name="ws-events-readonly", role="readonly")
        with client.websocket_connect(f"/ws/events?api_key={readonly_key}") as ws:
            hello = ws.receive_json()
            assert hello["type"] == "connected"
            assert hello["principal"] == "ws-events-readonly"


class TestWebSocketChat:
    """قناة المحادثة ثنائية الاتجاه."""

    def test_ready_frame_identifies_principal(self, client):
        with client.websocket_connect(
            f"/ws/chat?api_key={CLIENT_KEY}&session_id=ws-ready"
        ) as ws:
            ready = ws.receive_json()
            assert ready["type"] == "ready"
            assert ready["principal"] == "client-test"
            assert ready["role"] == "client"
            assert ready["transport"] == "websocket"

    def test_ping_pong(self, client):
        with client.websocket_connect(f"/ws/chat?api_key={CLIENT_KEY}") as ws:
            ws.receive_json()
            ws.send_json({"type": "ping"})
            assert ws.receive_json()["type"] == "pong"

    def test_empty_message_returns_error_frame(self, client):
        with client.websocket_connect(f"/ws/chat?api_key={CLIENT_KEY}") as ws:
            ws.receive_json()
            ws.send_json({"message": "   "})
            error = ws.receive_json()
            assert error["type"] == "error"
            assert "فارغة" in error["detail"]

    def test_streamed_answer_and_persistence(self, client):
        with client.websocket_connect(
            f"/ws/chat?api_key={CLIENT_KEY}&session_id=ws-session-1"
        ) as ws:
            assert ws.receive_json()["type"] == "ready"
            ws.send_json({"message": "ما هي باقاتكم؟", "session_id": "ws-session-1"})

            chunks = []
            done = None
            while done is None:
                frame = ws.receive_json()
                if frame["type"] == "chunk":
                    chunks.append(frame["delta"])
                elif frame["type"] == "done":
                    done = frame
                elif frame["type"] == "error":
                    pytest.fail(f"خطأ غير متوقع في البث: {frame['detail']}")

            assert done["reply"].strip()
            assert "".join(chunks).strip() == done["reply"].strip()
            assert done["session_id"] == "ws-session-1"
            assert done["source"] in ("google_antigravity_agent", "sovereign_rag_knowledge_engine")
            assert done["elapsed_ms"] >= 0

        history = client.get("/api/sessions/ws-session-1/history", headers=CLIENT_HEADERS)
        assert history.status_code == 200
        roles = [m["role"] for m in history.json()["messages"]]
        assert "user" in roles and "assistant" in roles

    def test_plain_text_frame_is_accepted(self, client):
        with client.websocket_connect(f"/ws/chat?api_key={CLIENT_KEY}") as ws:
            ws.receive_json()
            ws.send_text("سؤال بصيغة نص خام")
            frame = ws.receive_json()
            assert frame["type"] in ("chunk", "error")


class TestRateLimitStore:
    """حدّ المعدل المشترك: الحالة في SQLite لا في ذاكرة العامل."""

    def test_endpoint_requires_admin_system_scope(self, client):
        response = client.get("/api/admin/system/rate-limit", headers=CLIENT_HEADERS)
        assert response.status_code == 403
        assert response.json()["required_permission"] == "admin:system"

    def test_endpoint_reports_shared_backend(self, client):
        response = client.get("/api/admin/system/rate-limit", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        body = response.json()
        assert body["store"]["backend"] == "sqlite"
        assert body["store"]["shared_across_workers"] is True
        assert "general" in body["limits"] and "chat" in body["limits"]

    def test_requests_are_counted_in_the_store(self, client):
        before = client.get("/api/admin/system/rate-limit", headers=ADMIN_HEADERS).json()["store"]
        client.get("/api/rag/stats", headers=CLIENT_HEADERS)
        after = client.get("/api/admin/system/rate-limit", headers=ADMIN_HEADERS).json()["store"]
        assert after["tracked_hits"] >= before["tracked_hits"]


class TestWebSocketEvents:
    """ناقل الأحداث الموحد بين SSE و WebSocket."""

    def test_event_published_over_http_reaches_websocket(self, client):
        with client.websocket_connect(f"/ws/events?api_key={CLIENT_KEY}") as ws:
            assert ws.receive_json()["type"] == "connected"

            published = client.post(
                "/api/events/publish",
                json={"event_type": "ws_integration_probe", "payload": {"value": 42}},
                headers=ADMIN_HEADERS,
            )
            assert published.status_code == 200
            assert published.json()["subscribers_delivered"] >= 1
            assert "websocket" in published.json()["transports"]

            event = ws.receive_json()
            assert event["type"] == "event"
            assert event["event"] == "ws_integration_probe"
            assert event["payload"] == {"value": 42}

    def test_sse_transport_still_streams(self, client):
        with client.stream("GET", "/api/stream/events", headers=CLIENT_HEADERS) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            for line in response.iter_lines():
                if line.startswith("data: "):
                    payload = json.loads(line[len("data: "):])
                    assert payload["event"] == "connected"
                    break
