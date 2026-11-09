"""Proxy manager — store, validate, rotate."""

import asyncio
import httpx
import random
import time
from typing import Optional
from dataclasses import dataclass, field

from .database import db
from .proxy_fetcher import ProxyRaw


@dataclass
class ProxyRecord:
    id: int
    ip: str
    port: int
    protocol: str
    anonymity: str
    country: str
    source: str
    latency_ms: float
    is_alive: bool
    created_at: float
    last_checked: float
    fail_count: int

    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.ip}:{self.port}"


# ── CRUD ────────────────────────────────────────────────────────────────────

async def upsert_proxies(proxies: list[ProxyRaw]) -> int:
    """Insert or update proxies. Returns count inserted."""
    conn = await db.get()
    now = time.time()
    inserted = 0
    for p in proxies:
        await conn.execute(
            """INSERT OR REPLACE INTO proxies
               (ip, port, protocol, anonymity, country, source, created_at, is_alive)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (
                p.ip, p.port, p.protocol,
                p.anonymity, p.country, p.source, now,
            ),
        )
        inserted += 1
    await conn.commit()
    return inserted


async def get_all(limit: int = 500, offset: int = 0,
                  alive_only: bool = False) -> list[ProxyRecord]:
    conn = await db.get()
    query = "SELECT * FROM proxies"
    params: list = []
    if alive_only:
        query += " WHERE is_alive = 1"
    query += " ORDER BY latency_ms ASC, fail_count ASC"
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
    return [ProxyRecord(**dict(row)) for row in rows]


async def get_stats() -> dict:
    conn = await db.get()
    async with conn.execute("SELECT COUNT(*) FROM proxies") as cursor:
        total = (await cursor.fetchone())[0]
    async with conn.execute("SELECT COUNT(*) FROM proxies WHERE is_alive = 1") as cursor:
        alive = (await cursor.fetchone())[0]
    async with conn.execute(
        "SELECT source, COUNT(*) as cnt FROM proxies GROUP BY source ORDER BY cnt DESC"
    ) as cursor:
        sources = await cursor.fetchall()
    async with conn.execute(
        "SELECT country, COUNT(*) as cnt FROM proxies WHERE country != '' "
        "GROUP BY country ORDER BY cnt DESC LIMIT 10"
    ) as cursor:
        countries = await cursor.fetchall()
    async with conn.execute(
        "SELECT COUNT(*) FROM proxies WHERE fail_count > 3"
    ) as cursor:
        failed = (await cursor.fetchone())[0]
    return {
        "total": total,
        "alive": alive,
        "dead": total - alive,
        "failed": failed,
        "sources": [{"name": row[0], "count": row[1]} for row in sources],
        "top_countries": [{"name": row[0], "count": row[1]} for row in countries],
    }


async def get_recent_logs(limit: int = 50) -> list[dict]:
    conn = await db.get()
    async with conn.execute(
        "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?", (limit,)
    ) as cursor:
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def add_log(action: str, proxy: str = "", target_ip: str = "", result: str = ""):
    conn = await db.get()
    await conn.execute(
        "INSERT INTO logs (action, proxy, target_ip, result, created_at) VALUES (?, ?, ?, ?, ?)",
        (action, proxy, target_ip, result, time.time()),
    )
    await conn.commit()


# ── Validation ──────────────────────────────────────────────────────────────

TEST_URLS = [
    "https://api.ipify.org?format=text",
    "https://ifconfig.me/ip",
    "https://icanhazip.com",
]


async def validate_proxy(proxy: ProxyRecord, timeout: float = 8.0) -> tuple[bool, float]:
    """Check if proxy is alive and measure latency. Returns (is_alive, latency_ms)."""
    proxy_url = proxy.url
    for test_url in TEST_URLS:
        try:
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=timeout,
                follow_redirects=True,
            ) as client:
                start = time.time()
                r = await client.get(test_url)
                latency = (time.time() - start) * 1000
                if 200 <= r.status_code < 400:
                    return True, latency
        except Exception:
            continue
    return False, 0.0


async def bulk_validate(batch_size: int = 30, concurrency: int = 20) -> dict:
    """Validate proxies in batch. Returns stats."""
    all_proxies = await get_all(limit=2000)
    alive_before = sum(1 for p in all_proxies if p.is_alive)
    validated = 0
    new_alive = 0

    async def _check(p: ProxyRecord):
        nonlocal validated, new_alive
        is_alive, latency = await validate_proxy(p)
        conn = await db.get()
        await conn.execute(
            """UPDATE proxies SET is_alive = ?, latency_ms = ?,
               last_checked = ?, fail_count = CASE WHEN ? THEN fail_count + 1 ELSE 0 END
               WHERE id = ?""",
            (int(is_alive), latency, time.time(), int(not is_alive), p.id),
        )
        await conn.commit()
        if is_alive:
            new_alive += 1
        validated += 1
        if validated % 20 == 0:
            print(f"  Validated {validated}/{len(all_proxies)}...")

    tasks = [asyncio.create_task(_check(p)) for p in all_proxies]
    for i in range(0, len(tasks), concurrency):
        await asyncio.gather(*tasks[i:i + concurrency])

    await add_log("bulk_validate", result=f"validated={validated} new_alive={new_alive}")
    return {
        "validated": validated,
        "new_alive": new_alive,
        "alive_before": alive_before,
        "alive_after": alive_before + new_alive,
    }


# ── Rotation ────────────────────────────────────────────────────────────────

class Rotator:
    def __init__(self):
        self._index = 0
        self._lock = asyncio.Lock()
        self._pool: list[ProxyRecord] = []
        self._pool_loaded = False
        self._pool_fails: dict[int, int] = {}

    async def refresh_pool(self) -> list[ProxyRecord]:
        """Load alive proxies into in-memory pool (sorted by latency)."""
        self._pool = await get_all(alive_only=True, limit=1000)
        self._pool_fails = {}
        return self._pool

    async def ensure_pool(self) -> list[ProxyRecord]:
        """Load pool on first use, refresh if empty."""
        if not self._pool_fails and not self._pool:
            await self.refresh_pool()
        return self._pool

    async def get_next(self) -> Optional[ProxyRecord]:
        """Get next alive proxy in round-robin order (in-memory pool)."""
        async with self._lock:
            if not self._pool:
                proxies = await self.refresh_pool()
            else:
                proxies = self._pool
            if not proxies:
                return None
            proxy = proxies[self._index % len(proxies)]
            self._index = (self._index + 1) % len(proxies)
            return proxy

    async def get_random(self) -> Optional[ProxyRecord]:
        proxies = await self.refresh_pool()
        if not proxies:
            return None
        return random.choice(proxies)


rotator = Rotator()


# ── Request helpers ─────────────────────────────────────────────────────────

async def request_with_proxy(method: str, url: str, timeout: float = 15,
                              **kwargs) -> dict:
    """Make a request rotating through alive proxies."""
    proxy = await rotator.get_next()
    if not proxy:
        return {"error": "No alive proxies available", "status": 503}

    proxy_url = proxy.url
    kwargs.setdefault("proxy", proxy_url)
    kwargs.setdefault("timeout", timeout)
    kwargs.setdefault("follow_redirects", True)
    kwargs.setdefault("headers", {**{"User-Agent": "Mozilla/5.0"}, **kwargs.get("headers", {})})

    try:
        async with httpx.AsyncClient(**kwargs) as client:
            resp = await client.request(method, url)
            await add_log(method, proxy=proxy.url, target_ip=url,
                          result=f"status={resp.status_code} latency={resp.elapsed.total_seconds()*1000:.0f}ms")
            return {
                "status": resp.status_code,
                "body": resp.text[:2000],
                "proxy": proxy.url,
                "proxy_id": proxy.id,
                "latency_ms": round(resp.elapsed.total_seconds() * 1000, 1),
            }
    except Exception as e:
        # Decrement fail count (proxy failed)
        conn = await db.get()
        await conn.execute(
            "UPDATE proxies SET fail_count = fail_count + 1, is_alive = 0 WHERE id = ?",
            (proxy.id,),
        )
        await conn.commit()
        await add_log(method, proxy=proxy.url, target_ip=url, result=f"error: {e}")
        return {"error": str(e), "proxy": proxy.url, "status": 0}


async def probe_ip() -> dict:
    """Check what IP the current proxy rotation shows."""
    result = await request_with_proxy("GET", "https://api.ipify.org?format=json")
    if "error" in result:
        return result
    result["self_ip"] = (await request_with_proxy("GET", "https://api.ipify.org?format=text"))
    return result
