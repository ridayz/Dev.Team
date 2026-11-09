"""FastAPI Proxy Rotator Dashboard — Main Application."""

import asyncio
import time
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .proxy_fetcher import fetch_all
from .proxy_manager import (
    upsert_proxies, get_all, get_stats, get_recent_logs,
    bulk_validate, rotator, request_with_proxy, add_log,
)

DB_PATH = "/home/don-ai/Documents/Dev.Team/projects/proxy-rotator/src/proxies.db"


class ProxyTestRequest(BaseModel):
    url: str = "https://httpbin.org/ip"
    method: str = "GET"


class GmailCreateRequest(BaseModel):
    email: str
    password: str
    proxy_url: Optional[str] = None


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    from .database import db
    await db.connect()
    app.state.db = db
    yield
    await db.close()


# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(title="Proxy Rotator Dashboard", version="2.0", lifespan=lifespan)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ═══════════════════════════════════════════════════════════════════════════
#  API Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html")) as f:
        html = f.read()
    return HTMLResponse(html)


@app.get("/api/stats", response_model=dict)
async def api_stats():
    return await get_stats()


@app.get("/api/proxies")
async def api_proxies(
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    alive_only: bool = False,
    source: str = Query("", description="Filter by source"),
    sort: str = Query("latency", description="latency|fail_count|created|country"),
    order: str = Query("asc", description="asc|desc"),
):
    proxies = await get_all(limit=limit, offset=offset, alive_only=alive_only)
    if source:
        proxies = [p for p in proxies if p.source == source]
    reverse = order == "desc"
    if sort == "latency":
        proxies.sort(key=lambda p: p.latency_ms, reverse=reverse)
    elif sort == "fail_count":
        proxies.sort(key=lambda p: p.fail_count, reverse=reverse)
    elif sort == "country":
        proxies.sort(key=lambda p: p.country, reverse=reverse)
    else:
        proxies.sort(key=lambda p: p.created_at, reverse=reverse)
    return {"proxies": [p.__dict__ for p in proxies], "total": len(proxies)}


@app.post("/api/proxies/fetch", response_model=dict)
async def api_fetch_proxies(limit: int = Query(500, ge=50, le=5000)):
    """Fetch free proxies from multiple sources concurrently."""
    result = await fetch_all(limit=limit)
    count = await upsert_proxies(result["proxies"])
    await add_log("fetch", result=f"fetched={result['stats'].get('total_unique', 0)} inserted={count}")
    return {"fetched": result["stats"]["total_unique"], "inserted": count, "sources": result["stats"]}


@app.post("/api/proxies/validate", response_model=dict)
async def api_validate():
    """Validate all stored proxies (alive check + latency)."""
    return await bulk_validate(concurrency=25)


@app.get("/api/proxies/{proxy_id}/test")
async def api_test_proxy(proxy_id: int):
    from .database import db
    conn = await db.get()
    row = await conn.execute("SELECT * FROM proxies WHERE id = ?", (proxy_id,))
    p = await row.fetchone()
    if not p:
        raise HTTPException(404, "Proxy not found")
    import httpx
    proxy_url = f"{p['protocol']}://{p['ip']}:{p['port']}"
    try:
        async with httpx.AsyncClient(proxy=proxy_url, timeout=10) as c:
            r = await c.get("https://api.ipify.org?format=text")
            latency = r.elapsed.total_seconds() * 1000
            ip = r.text.strip()
            await conn.execute(
                "UPDATE proxies SET is_alive=1, latency_ms=?, last_checked=? WHERE id=?",
                (latency, time.time(), proxy_id),
            )
            await conn.commit()
            await add_log("test_single", proxy=proxy_url, target_ip=ip,
                          result=f"status=200 latency={latency:.0f}ms")
            return {"proxy_url": proxy_url, "exit_ip": ip, "latency_ms": round(latency, 1), "alive": True}
    except Exception as e:
        await conn.execute("UPDATE proxies SET is_alive=0, fail_count=fail_count+1 WHERE id=?", (proxy_id,))
        await conn.commit()
        return {"proxy_url": proxy_url, "error": str(e), "alive": False}


@app.post("/api/proxies/test-request")
async def api_test_request(req: ProxyTestRequest):
    """Send a test request using the proxy rotator."""
    return await request_with_proxy(req.method, req.url)


@app.delete("/api/proxies/clear-dead")
async def api_clear_dead():
    from .database import db
    conn = await db.get()
    await conn.execute("DELETE FROM proxies WHERE is_alive = 0")
    deleted = await conn.execute("DELETE FROM proxies WHERE fail_count > 5")
    await conn.commit()
    count = deleted.rowcount if hasattr(deleted, 'rowcount') else 0
    await add_log("clear_dead", result=f"removed={count}")
    return {"removed": count}


@app.delete("/api/proxies/clear-all")
async def api_clear_all():
    from .database import db
    conn = await db.get()
    await conn.execute("DELETE FROM proxies")
    await conn.commit()
    await add_log("clear_all", result="all proxies removed")
    return {"message": "All proxies cleared"}


@app.delete("/api/proxies/{proxy_id}")
async def api_delete_proxy(proxy_id: int):
    from .database import db
    conn = await db.get()
    await conn.execute("DELETE FROM proxies WHERE id = ?", (proxy_id,))
    await conn.commit()
    return {"deleted": proxy_id}


@app.get("/api/logs")
async def api_logs(limit: int = Query(100, ge=1, le=500)):
    return {"logs": await get_recent_logs(limit)}


@app.get("/api/rotate/test")
async def api_rotate_test(url: str = "https://api.ipify.org?format=json"):
    result = await request_with_proxy("GET", url)
    return result


@app.post("/api/gmail/create")
async def api_gmail_create(req: GmailCreateRequest):
    """Gmail account creation via proxy rotator (anti-detect proxy layer)."""
    result = await request_with_proxy("POST", "https://accounts.google.com/")
    await add_log("GMAIL", proxy=result.get("proxy", ""), target_ip=req.email,
                  result=f"status={result.get('status')}")
    return {
        "email": req.email,
        "proxy": result.get("proxy"),
        "status": result.get("status"),
        "ok": result.get("status", 0) == 200,
    }


@app.post("/api/gmail/create-real")
async def api_gmail_create_real(req: GmailCreateRequest):
    """Real Gmail account creation via Playwright anti-detect browser + proxy."""
    from .gmail_creator import create_gmail_account
    proxy_url = req.proxy_url
    if not proxy_url:
        proxy_result = await request_with_proxy("GET", "https://accounts.google.com")
        proxy_url = proxy_result.get("proxy") if proxy_result.get("status") == 200 else None
    result = await create_gmail_account(req.email, req.password, proxy_url=proxy_url)
    await add_log("GMAIL_REAL", proxy=proxy_url or "", target_ip=req.email, result=f"ok={result.get('ok')}")
    return {**result, "proxy": proxy_url}


@app.post("/api/gmail/connect")
async def api_gmail_connect():
    """Connect to a proxy for Gmail flow (via rotator)."""
    result = await request_with_proxy("GET", "https://accounts.google.com")
    return result


@app.post("/api/gmail/disconnect")
async def api_gmail_disconnect():
    """Disconnect proxy for Gmail flow (release alive proxies)."""
    from .database import db
    conn = await db.get()
    await conn.execute("DELETE FROM proxies WHERE is_alive = 1")
    await conn.commit()
    await add_log("GMAIL_DISCONNECT", result="proxy released")
    return {"ok": True}


# ═══════════════════════════════════════════════════════════════════════════
#  CORS / Middleware
# ═══════════════════════════════════════════════════════════════════════════

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)
