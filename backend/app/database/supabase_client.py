from __future__ import annotations

import httpx

from app.config.settings import settings

_http_client = httpx.Client(
    timeout=httpx.Timeout(30, connect=10),
    limits=httpx.Limits(max_connections=30, max_keepalive_connections=15),
)


class SupabaseRESTClient:
    """Small PostgREST client that preserves the authenticated user's RLS context."""

    def __init__(self, token: str):
        if not settings.supabase_url or not settings.supabase_publishable_key:
            raise RuntimeError("Supabase no está configurado en backend/.env.")

        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_publishable_key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get(
        self,
        table: str,
        *,
        select: str = "*",
        filters: dict[str, str] | None = None,
        order: str | None = None,
        limit: int = 500,
    ) -> list[dict]:
        params: dict[str, str] = {"select": select, "limit": str(limit)}
        if filters:
            params.update(filters)
        if order:
            params["order"] = order

        response = _http_client.get(
            f"{self.base_url}/{table}",
            headers=self.headers,
            params=params,
        )

        self._raise_for_supabase_error(response)
        return response.json()

    def get_all(
        self,
        table: str,
        *,
        select: str = "*",
        filters: dict[str, str] | None = None,
        order: str | None = None,
        page_size: int = 1000,
    ) -> list[dict]:
        """Read every visible row without silently truncating analytics."""
        rows: list[dict] = []
        offset = 0
        while True:
            params: dict[str, str] = {
                "select": select,
                "limit": str(page_size),
                "offset": str(offset),
            }
            if filters:
                params.update(filters)
            if order:
                params["order"] = order
            response = _http_client.get(
                f"{self.base_url}/{table}", headers=self.headers, params=params
            )
            self._raise_for_supabase_error(response)
            batch = response.json()
            rows.extend(batch)
            if len(batch) < page_size:
                return rows
            offset += page_size

    def insert(self, table: str, payload: dict) -> list[dict]:
        headers = {**self.headers, "Prefer": "return=representation"}
        response = _http_client.post(
            f"{self.base_url}/{table}",
            headers=headers,
            json=payload,
        )

        self._raise_for_supabase_error(response)
        return response.json() if response.content else []

    def update(
        self, table: str, payload: dict, *, filters: dict[str, str]
    ) -> list[dict]:
        headers = {**self.headers, "Prefer": "return=representation"}
        response = _http_client.patch(
            f"{self.base_url}/{table}",
            headers=headers,
            params=filters,
            json=payload,
        )
        self._raise_for_supabase_error(response)
        return response.json() if response.content else []

    def delete(self, table: str, *, filters: dict[str, str]) -> list[dict]:
        """Delete only explicitly filtered rows and return affected records."""
        if not filters:
            raise ValueError("Una eliminación requiere al menos un filtro.")
        headers = {**self.headers, "Prefer": "return=representation"}
        response = _http_client.delete(
            f"{self.base_url}/{table}",
            headers=headers,
            params=filters,
        )
        self._raise_for_supabase_error(response)
        return response.json() if response.content else []

    def upsert(
        self, table: str, payload: list[dict], *, on_conflict: str | None = None
    ) -> list[dict]:
        headers = {
            **self.headers,
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        params = {"on_conflict": on_conflict} if on_conflict else None
        response = _http_client.post(
            f"{self.base_url}/{table}",
            headers=headers,
            params=params,
            json=payload,
            timeout=60,
        )
        self._raise_for_supabase_error(response)
        return response.json() if response.content else []

    def rpc(self, function: str, payload: dict | None = None) -> object:
        response = _http_client.post(
            f"{self.base_url}/rpc/{function}",
            headers=self.headers,
            json=payload or {},
        )
        self._raise_for_supabase_error(response)
        return response.json() if response.content else None

    def upload(self, bucket: str, path: str, content: bytes, content_type: str) -> str:
        headers = {"apikey": settings.supabase_publishable_key, "Authorization": self.headers["Authorization"], "Content-Type": content_type, "x-upsert": "false"}
        response = _http_client.post(f"{settings.supabase_url}/storage/v1/object/{bucket}/{path}", headers=headers, content=content)
        self._raise_for_supabase_error(response)
        return f"{settings.supabase_url}/storage/v1/object/public/{bucket}/{path}"

    def count(self, table: str, filters: dict[str, str] | None = None) -> int:
        params: dict[str, str] = {"select": "*", "limit": "1"}
        if filters:
            params.update(filters)

        headers = {
            **self.headers,
            "Prefer": "count=exact",
            "Range": "0-0",
        }

        response = _http_client.get(
            f"{self.base_url}/{table}",
            headers=headers,
            params=params,
        )

        self._raise_for_supabase_error(response)
        content_range = response.headers.get("content-range", "")
        try:
            return int(content_range.rsplit("/", 1)[1])
        except (IndexError, ValueError):
            return len(response.json())

    @staticmethod
    def _raise_for_supabase_error(response: httpx.Response) -> None:
        if response.is_success:
            return

        try:
            body = response.json()
            detail = body.get("message") or body.get("hint") or response.text
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"Supabase respondió {response.status_code}: {detail}"
        )
