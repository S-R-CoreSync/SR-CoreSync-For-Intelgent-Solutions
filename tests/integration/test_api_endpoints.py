"""
=============================================================================
اختبارات تكامل لنقاط نهاية API (sr_agent_server.py)
=============================================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient

# تعيين متغيرات البيئة قبل استيراد الخادم
import os
os.environ["GEMINI_API_KEY"] = "test-dummy-key"
os.environ["CORESYNC_API_KEYS"] = "admin-test:sk-admin-secret-123:admin,client-test:sk-client-secret-456:client"
os.environ["CORESYNC_AUTH_DISABLED"] = "0"
os.environ["CORESYNC_RATE_LIMIT"] = "1000/min"
os.environ["CORESYNC_CHAT_RATE_LIMIT"] = "100/min"

from sr_agent_server import app


class TestHealthEndpoints:
    """اختبارات نقاط نهاية فحص الحالة."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as client:
            yield client

    def test_root_endpoint(self, client):
        """يجب أن يعيد نقطة الجذر حالة الخادم."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data

    def test_health_endpoint(self, client):
        """يجب أن يعيد نقطة /health حالة جيدة."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuthentication:
    """اختبارات المصادقة والتحكم بالوصول."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def admin_headers(self):
        return {"X-API-Key": "sk-admin-secret-123"}

    @pytest.fixture
    def client_headers(self):
        return {"X-API-Key": "sk-client-secret-456"}

    def test_rag_stats_without_key(self, client):
        """يجب رفض الوصول بدون مفتاح API."""
        response = client.get("/api/rag/stats")
        assert response.status_code == 401

    def test_rag_stats_with_client_key(self, client, client_headers):
        """يجب السماح للمفتاح العميل بالوصول لإحصائيات راغ."""
        response = client.get("/api/rag/stats", headers=client_headers)
        assert response.status_code == 200

    def test_sessions_with_client_key_forbidden(self, client, client_headers):
        """يجب رفض الوصول لمسارات الإدارة بمفتاح عميل."""
        response = client.get("/api/sessions", headers=client_headers)
        assert response.status_code == 403

    def test_sessions_with_admin_key(self, client, admin_headers):
        """يجب السماح للمفتاح الإداري بالوصول لجلسات المستخدمين."""
        response = client.get("/api/sessions", headers=admin_headers)
        assert response.status_code == 200

    def test_invalid_api_key(self, client):
        """يجب رفض المفتاح غير الصالح."""
        response = client.get("/api/rag/stats", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 401


class TestChatEndpoints:
    """اختبارات نقاط نهاية المحادثة."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def client_headers(self):
        return {"X-API-Key": "sk-client-secret-456"}

    def test_chat_endpoint(self, client, client_headers):
        """يجب معالجة طلب المحادثة بنجاح."""
        response = client.post(
            "/api/chat",
            json={"message": "ما هي باقاتكم؟", "session_id": "test-session-1"},
            headers=client_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "session_id" in data
        assert "timestamp" in data

    def test_chat_empty_message(self, client, client_headers):
        """should reject empty message."""
        response = client.post(
            "/api/chat",
            json={"message": "", "session_id": "test-session-2"},
            headers=client_headers,
        )
        assert response.status_code == 400

    def test_chat_stream_endpoint(self, client, client_headers):
        """يجب دعم بث SSE للمحادثة."""
        response = client.get(
            "/api/chat/stream?message=مرحبا&session_id=test-stream-1",
            headers=client_headers,
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestWorkspacePortals:
    """اختبارات نقاط نهاية بوابات مساحة العمل."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def client_headers(self):
        return {"X-API-Key": "sk-client-secret-456"}

    def test_workspace_portals(self, client, client_headers):
        """يجب إرجاع قائمة بوابات المشروع."""
        response = client.get("/api/workspace/portals", headers=client_headers)
        assert response.status_code == 200
        data = response.json()
        assert "portals_summary" in data