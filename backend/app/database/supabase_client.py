from __future__ import annotations

import httpx

from app.config.settings import settings


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

        with httpx.Client(timeout=30) as client:
            response = client.get(
                f"{self.base_url}/{table}",
                headers=self.headers,
                params=params,
            )

        self._raise_for_supabase_error(response)
        return response.json()

    def insert(self, table: str, payload: dict) -> list[dict]:
        headers = {**self.headers, "Prefer": "return=representation"}
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{self.base_url}/{table}",
                headers=headers,
                json=payload,
            )

        self._raise_for_supabase_error(response)
        return response.json() if response.content else []

    def count(self, table: str, filters: dict[str, str] | None = None) -> int:
        params: dict[str, str] = {"select": "*", "limit": "1"}
        if filters:
            params.update(filters)

        headers = {
            **self.headers,
            "Prefer": "count=exact",
            "Range": "0-0",
        }

        with httpx.Client(timeout=30) as client:
            response = client.get(
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
