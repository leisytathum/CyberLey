def list_response(items: list[dict]) -> dict:
    return {"items": items, "total": len(items)}
