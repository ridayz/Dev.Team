# 0001. Dark fiber core manager: Python stdlib + SQLite + vanilla frontend

- **Date:** 2026-11-09
- **Status:** accepted
- **Context:** Butuh dashboard manajemen core backbone 96/288/576 untuk lease dark fiber tenant. Environment tidak menyediakan Node.js/npm, dan dashboard harus bisa dipakai tanpa langkah instalasi tambahan.
- **Choice:** Backend Python 3 standard library (`http.server`, `sqlite3`) yang sekaligus menyajikan frontend statis. Frontend HTML/CSS/JS vanilla tanpa CDN atau build step. Core kabel diturunkan dari kapasitas + kode warna 12 fiber TIA-598; lease disimpan per core dengan `batch_id`.
- **Reason:** Python 3.12 dan SQLite sudah tersedia. Satu proses menghilangkan CORS dan build tooling. Data 576 core tetap ringan karena grid dihitung, bukan disimpan per baris. `batch_id` mendukung alokasi/perpanjangan/pelepasan beberapa core sekaligus.
- **Consequence:** Tidak ada ekosistem framework, hot reload, atau TypeScript. Skala data cocok untuk satu tim operasi; jika butuh multi-user/auth atau integrasi OSS, backend perlu diganti/ditambah lapisan API.
