"""
إدارة مفاتيح API المتقدمة (Advanced API Key Management)
S&R CoreSync For Intelligent Solutions
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("sr_auth_advanced")

PERMISSIONS: Dict[str, List[str]] = {
    "admin": ["chat:read","chat:write","sessions:read","sessions:write","sessions:delete","rag:read","rag:write","rag:reindex","upload:write","appeals:read","appeals:write","events:publish","subagent:read","subagent:run","admin:keys","admin:system"],
    "client": ["chat:read","chat:write","sessions:read","rag:read"],
    "readonly": ["chat:read","sessions:read","rag:read"],
}


def has_permission(role: str, permission: str) -> bool:
    return permission in PERMISSIONS.get(role, [])


class AdvancedKeyEntry:
    def __init__(self, name: str, role: str, key_sha256: str,
                 plain_key: Optional[str] = None, expires_at: Optional[str] = None,
                 permissions: Optional[List[str]] = None, is_revoked: bool = False,
                 created_at: Optional[str] = None, usage_count: int = 0,
                 last_used_at: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.role = role
        self.key_sha256 = key_sha256
        self.plain_key = plain_key
        self.expires_at = expires_at
        self.permissions = permissions or PERMISSIONS.get(role, [])
        self.is_revoked = is_revoked
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.usage_count = usage_count
        self.last_used_at = last_used_at
        self.metadata = metadata or {}

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        try:
            return datetime.now(timezone.utc) > datetime.fromisoformat(self.expires_at)
        except Exception:
            return False

    def is_valid(self) -> bool:
        return not self.is_revoked and not self.is_expired()

    def record_usage(self) -> None:
        self.usage_count += 1
        self.last_used_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "role": self.role, "key_sha256": self.key_sha256,
                "expires_at": self.expires_at, "permissions": self.permissions,
                "is_revoked": self.is_revoked, "created_at": self.created_at,
                "usage_count": self.usage_count, "last_used_at": self.last_used_at,
                "metadata": self.metadata}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdvancedKeyEntry":
        return cls(name=data["name"], role=data["role"], key_sha256=data["key_sha256"],
                   expires_at=data.get("expires_at"), permissions=data.get("permissions"),
                   is_revoked=data.get("is_revoked", False), created_at=data.get("created_at"),
                   usage_count=data.get("usage_count", 0), last_used_at=data.get("last_used_at"),
                   metadata=data.get("metadata", {}))


class AdvancedKeyStore:
    def __init__(self, auth_file: Optional[str] = None):
        self.auth_file = Path(auth_file) if auth_file else Path(__file__).resolve().parent / "auth_keys.json"
        self._entries: Dict[str, AdvancedKeyEntry] = {}
        self.auth_enabled: bool = False
        self._load()

    def _load(self) -> None:
        try:
            if self.auth_file.is_file():
                data = json.loads(self.auth_file.read_text(encoding="utf-8"))
                count = 0
                for entry_data in data.get("keys", []):
                    entry = AdvancedKeyEntry.from_dict(entry_data)
                    self._entries[entry.key_sha256] = entry
                    count += 1
                if count:
                    logger.info("تم تحميل %d مفتاح API من %s", count, self.auth_file)
        except Exception as exc:
            logger.error("تعذر تحميل ملف المصادقة %s: %s", self.auth_file, exc)
        env_keys = os.getenv("CORESYNC_API_KEYS", "").strip()
        if env_keys:
            count = 0
            for spec in env_keys.split(","):
                parts = [p.strip() for p in spec.split(":") if p.strip()]
                if len(parts) < 2:
                    continue
                name, plain = parts[0], parts[1]
                role = parts[2] if len(parts) >= 3 else "client"
                digest = hashlib.sha256(plain.encode("utf-8")).hexdigest()
                self._entries[digest] = AdvancedKeyEntry(name=name, role=role, key_sha256=digest, plain_key=plain)
                count += 1
            if count:
                logger.info("تم تحميل %d مفتاح من CORESYNC_API_KEYS", count)
        self.auth_enabled = bool(self._entries)

    def save_to_file(self) -> None:
        data = {"keys": [e.to_dict() for e in self._entries.values()]}
        self.auth_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("تم حفظ %d مفتاح في %s", len(self._entries), self.auth_file)

    def add_key(self, name: str, plain_key: str, role: str = "client",
                expires_in_days: Optional[int] = None,
                permissions: Optional[List[str]] = None,
                metadata: Optional[Dict[str, Any]] = None) -> str:
        key_sha256 = hashlib.sha256(plain_key.encode("utf-8")).hexdigest()
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat()
        entry = AdvancedKeyEntry(name=name, role=role, key_sha256=key_sha256,
                                 plain_key=plain_key, expires_at=expires_at,
                                 permissions=permissions, metadata=metadata or {})
        self._entries[key_sha256] = entry
        self.save_to_file()
        logger.info("تم إضافة مفتاح: %s (الدور: %s)", name, role)
        return plain_key

    def revoke_key(self, key_sha256: str) -> bool:
        if key_sha256 in self._entries:
            self._entries[key_sha256].is_revoked = True
            self.save_to_file()
            logger.info("تم إلغاء المفتاح: %s...", key_sha256[:16])
            return True
        return False

    def rotate_key(self, old_key_sha256: str, new_plain_key: str) -> Optional[str]:
        if old_key_sha256 not in self._entries:
            return None
        old = self._entries[old_key_sha256]
        new_sha = hashlib.sha256(new_plain_key.encode("utf-8")).hexdigest()
        new_entry = AdvancedKeyEntry(name=old.name, role=old.role, key_sha256=new_sha,
                                     plain_key=new_plain_key, expires_at=old.expires_at,
                                     permissions=old.permissions, metadata=old.metadata)
        del self._entries[old_key_sha256]
        self._entries[new_sha] = new_entry
        self.save_to_file()
        return new_plain_key

    def authenticate(self, presented_key: str) -> Optional[Tuple[AdvancedKeyEntry, str]]:
        if not presented_key:
            return None
        digest = hashlib.sha256(presented_key.encode("utf-8")).hexdigest()
        for sha, entry in self._entries.items():
            if digest == sha:
                if not entry.is_valid():
                    return None
                entry.record_usage()
                self.save_to_file()
                return entry, digest
        return None

    def get_key_info(self, key_sha256: str) -> Optional[Dict[str, Any]]:
        entry = self._entries.get(key_sha256)
        if not entry:
            return None
        return {"name": entry.name, "role": entry.role, "permissions": entry.permissions,
                "is_revoked": entry.is_revoked, "is_expired": entry.is_expired(),
                "is_valid": entry.is_valid(), "created_at": entry.created_at,
                "expires_at": entry.expires_at, "usage_count": entry.usage_count,
                "last_used_at": entry.last_used_at, "metadata": entry.metadata}

    def list_keys(self) -> List[Dict[str, Any]]:
        return [{"key_sha256": e.key_sha256, "name": e.name, "role": e.role,
                 "is_valid": e.is_valid(), "is_revoked": e.is_revoked,
                 "is_expired": e.is_expired(), "created_at": e.created_at,
                 "expires_at": e.expires_at, "usage_count": e.usage_count,
                 "last_used_at": e.last_used_at} for e in self._entries.values()]