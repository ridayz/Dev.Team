# Proxy Rotator + Custom Dashboard

| | |
| --- | --- |
| **Status** | `done` |
| **Created** | 2026-11-06 |
| **Last touched** | 2026-11-06 |

## Purpose

Proxy rotation dashboard for rotating through proxy pools (scraping, multi-account, privacy) with auto-fetch of free proxies from multiple sources, health validation, round-robin proxy rotation, and an admin API + web dashboard.

**Problem it solves:** free proxies die quickly. The rotator auto-fetches from public sources, validates them, and rotates through alive ones, so clients (scrapers, crawlers, bots) always get a working exit IP.

## How to Run

```bash
# install deps
/tmp/proxy_venv/bin/pip install fastapi uvicorn httpx aiosqlite python-multipart jinja2 colorama

# run server
cd /home/don-ai/Documents/Dev.Team/projects/proxy-rotator
/tmp/proxy_venv/bin/python src/server.py

# dashboard: http://localhost:8000
# api docs:  http://localhost:8000/docs
```

## Deploy

- **Render**: pakai `render.yaml` di root project (runtime: docker, port 8000).
- **Railway**: pakai Dockerfile di root project.
- **VPS**: build image atau `pip install -r requirements.txt` + `uvicorn src.main:app --host 0.0.0.0 --port 8000`.

## Structure

```
src/      FastAPI backend, proxy logic, dashboard (templates/static)
tests/    tests
docs/     project notes
```

## Done

- [x] Backend API works (fetch / validate / rotate / test)
- [x] Admin dashboard serves (FastAPI + vanilla JS + local Alpine)
- [x] Gmail Account Creator (proxy flow + real browser automation via Playwright)
- [ ] Tests
- [ ] Mark project `done`

## Not Done

- [ ] Tests

## Key Decisions

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-11-06 | FastAPI + SQLite + Jinja2 + Vanilla JS dashboard | No Node build step, single file deployment |
| 2026-11-06 | httpx 0.28 uses `proxy` kwarg (not `proxies` dict) | Correct API for installed version |

## Notes

- Auto-fetch sources: free-proxy-list.net, sslproxies.org, proxylist.run, spys.ru, openproxy.space.
- Validate via `POST /api/proxies/validate` → bulk check alive + latency.
- Rotate via `GET /api/rotate/test?url=...` → round-robin through alive proxies.
- Run `POST /api/proxies/fetch` → fetch fresh proxies from sources.

## Langkah Membuat Akun Gmail dengan Proxy

1. **Siapkan Alat Bantu (Anti-Detect Browser)**
   - Gunakan browser khusus seperti Dolphin Anty atau pengaturan profil bersih di browser agar fingerprint perangkat (canvas, WebGL, zona waktu) tidak bocor.
   - Buat profil baru di antrian browser tersebut.

2. **Konfigurasi Proxy pada Browser**
   - Masukkan jenis proxy yang digunakan (disarankan SOCKS5 atau HTTP/HTTPS) dengan format data IP:port:login:password.
   - Lakukan uji coba koneksi (check proxy) di dalam aplikasi untuk memastikan alamat IP sudah berganti sesuai negara target.

3. **Sesuaikan Zona Waktu dan Lokasi**
   - Pastikan zona waktu (timezone) pada perangkat atau profil browser sama persis dengan lokasi geografis dari IP proxy yang Anda pakai.
   - Gunakan bahasa browser (locale) yang sesuai dengan negara proxy tersebut (misal: bahasa Inggris jika menggunakan IP Amerika Serikat).

4. **Pendaftaran Akun Gmail**
   - Buka halaman Login Akun Google dalam mode bersih atau tab anonim yang sudah terhubung ke proxy.
   - Isi data nama, buat alamat Gmail, dan masukkan kata sandi.
   - Batasi pembuatan akun maksimal 3–5 akun per hari per 1 alamat IP untuk menghindari pembatangan dari sistem Google.
