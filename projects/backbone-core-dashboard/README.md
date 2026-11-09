# backbone-core-dashboard

| | |
| --- | --- |
| **Status** | `in-progress` |
| **Created** | 2026-11-09 |
| **Last touched** | 2026-11-09 |

## Purpose

Dashboard manajemen core kabel backbone fiber optik (96, 288, 576 core) untuk manajemen dark fiber tenant. Memantau ketersediaan core, alokasi ke tenant, rute kabel, dan status konektivitas tanpa autentikasi (full access dashboard management).

## How to Run

Backend (Python 3 + SQLite, built-in, tidak perlu install paket):

```bash
./run.sh
```

Atau jalankan manual:

```bash
cd src/server
python3 app.py
# Buka http://localhost:4000/api/health untuk memastikan siap
```

Frontend (vanilla HTML + Tailwind CDN, tidak perlu build):

```bash
# Buka file langsung di browser
open src/web/index.html

# Atau dengan live server agar proxy API berjalan pada origin yang sama:
cd src/web
python3 -m http.server 5173
# Buka http://localhost:5173
```

API backend berjalan di port 4000. Frontend memanggil `/api/*` langsung (relative), jadi paling mudah buka `src/web/index.html` langsung di browser, atau via live server di port beda (CORS sudah diatur di backend).

## Structure

```
src/
  server/
    app.py         Python HTTP server + SQLite (port 4000)
    backbone.db    SQLite database (dibuat otomatis saat pertama kali dijalankan)
  web/
    index.html     Frontend single-file (Tailwind CDN + Chart.js CDN + vanilla JS)
tests/             tests
docs/              project-specific notes
```

## Done

- [x] Project scaffolding
- [x] Backend API (cables, cores, tenants, allocations) dengan SQLite
- [x] Seed data (5 kabel: 96/288/576 core, 4 tenant, beberapa alokasi demo)
- [x] Frontend dashboard: statistik, chart utilisasi, daftar kabel, grid core, manajemen tenant, alokasi/release core
- [x] Tanpa login / full access dashboard management

## Not Done

- [ ] Export laporan (CSV/PDF)
- [ ] Peta rute backbone (GIS)
- [ ] Unit tests

## Key Decisions

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-11-09 | Python + SQLite (built-in) | Tidak ada Node.js/npm di environment; Python 3 bawaan Zorin OS siap pakai tanpa install |
| 2026-11-09 | HTML vanilla + Tailwind/Chart.js CDN | Tanpa build step, langsung dibuka di browser |
| 2026-11-09 | Tanpa login / auth | Permintaan user: full dashboard management tanpa multi-tenant isolation |
