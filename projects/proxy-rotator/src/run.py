"""Entry point launcher for standalone CLI."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.proxy_fetcher import fetch_all
from src.proxy_manager import bulk_validate, get_all, rotator, request_with_proxy, upsert_proxies


async def main():
    print("=" * 50)
    print("  Proxy Rotator CLI")
    print("=" * 50)

    print("\n[1] Fetching free proxies...")
    result = await fetch_all(limit=300)
    count = await upsert_proxies(result["proxies"])
    print(f"    OK Fetched {result['stats'].get('total_unique', 0)} unique from {len(result['stats'])-1} sources")
    print(f"    OK Inserted {count} into DB")

    print("\n[2] Validating proxies...")
    stats = await bulk_validate(concurrency=20)
    print(f"    OK Validated {stats['validated']}")
    print(f"    OK {stats['new_alive']} new alive proxies")

    alive = await get_all(alive_only=True, limit=20)
    print(f"\n[3] Top {min(20, len(alive))} alive proxies:")
    for p in alive[:20]:
        lat = f"{p.latency_ms:.0f}ms" if p.latency_ms > 0 else "—"
        print(f"    {p.ip}:{p.port:<8} {p.protocol:<6} {p.country:<4} {lat:>7}")

    print("\n[4] Testing rotation (5 requests)...")
    for i in range(5):
        r = await request_with_proxy("GET", "https://api.ipify.org?format=json")
        ip = (r.get("body") or "").strip().replace('"', '')
        print(f"    [{i+1}] IP: {ip:<40} via {r.get('proxy','')}")

    print("\nDONE!")


if __name__ == "__main__":
    asyncio.run(main())
