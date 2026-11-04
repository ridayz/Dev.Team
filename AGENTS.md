# AGENTS.md — Aturan Markas Dev.Team

File ini dibaca otomatis oleh setiap agent di folder ini. Isinya aturan main, bukan
dokumentasi. Kalau ragu, ikuti file ini.

## Peta markas

```
Dev.Team/
├── AGENTS.md              ← kamu di sini (aturan)
├── README.md              ← panduan untuk manusia
├── .opencode/
│   ├── agents/            ← definisi agent
│   └── skills/            ← skill (archify, unslop, ...)
├── projects/              ← semua proyek
│   ├── README.md          ← indeks + status
│   └── <nama-proyek>/
│       ├── README.md      ← tujuan, status, cara jalan
│       ├── src/           ← kode
│       ├── tests/         ← test
│       └── docs/          ← catatan khusus proyek ini
├── templates/new-project/ ← cetakan proyek baru
├── docs/
│   ├── decisions/         ← kenapa memilih A bukan B
│   ├── diagrams/          ← hasil skill archify
│   └── notes/             ← catatan lintas proyek
└── scripts/               ← helper (new-project.sh)
```

## Aturan penempatan file

| Jenis file | Taruh di | Jangan di |
| --- | --- | --- |
| Kode aplikasi | `projects/<nama>/src/` | root markas |
| Test | `projects/<nama>/tests/` | `src/` |
| Catatan proyek | `projects/<nama>/docs/` | `docs/` root |
| Diagram (archify) | `docs/diagrams/` | dalam proyek |
| Keputusan arsitektur | `docs/decisions/` | README proyek |
| Script bantu | `scripts/` | `src/` |
| Skill baru | `.opencode/skills/<id>/SKILL.md` | dalam proyek |

## Aturan yang tidak boleh dilanggar

1. **Jangan buat `.opencode/` di dalam `projects/*/`.** Satu `.opencode` di root sudah berlaku untuk semua.
2. **Jangan ubah `.opencode/skills/`** kecuali sedang memasang atau mengganti skill.
3. **Jangan hapus proyek** yang sudah ada. Tandai `selesai` atau `parkir` di indeks.
4. **Jangan taruh rahasia** (`.env`, token, password) di repo. Pakai `.env.example`.
5. **Jangan taruh file besar** (ISO, zip, video) di markas. Simpan di luar.

## Cara kerja yang diharapkan

1. Baca `projects/README.md` dulu untuk tahu konteks.
2. Baca `README.md` proyek yang disentuh.
3. Kalau pekerjaan lebih dari 3 langkah, tulis rencana singkat dulu.
4. Kerjakan per bagian, verifikasi tiap bagian.
5. Perbarui status di `projects/README.md` setelah selesai.

## Konvensi penamaan

| Item | Format | Contoh |
| --- | --- | --- |
| Folder proyek | huruf kecil, tanda hubung | `toko-online` |
| File kode | sesuai bahasa | `checkout.ts` |
| Catatan | `kebab-case.md` | `rencana-checkout.md` |
| Keputusan | `NNNN-judul.md` | `0001-pakai-postgres.md` |
| Diagram | `<proyek>-<jenis>.html` | `toko-online-arsitektur.html` |

## Status proyek

`rencana` → `dikerjakan` → `review` → `selesai` / `parkir`

## Skill

- Skill di-load lewat tool `skill` dengan ID (nama folder, case-sensitive).
- AGENTS.md tidak me-load skill. AGENTS.md hanya instruksi konteks penggunaan.
- Skill baru: taruh di `.opencode/skills/<id>/SKILL.md`, lalu daftarkan di `dev-team.md`.
- Muat hanya saat relevan. Kalau pengguna menyebut skill, muat dulu sebelum mulai.

## Definisi "selesai"

Sebuah tugas dianggap selesai kalau:
- kode jalan tanpa error,
- test/lint lulus (kalau ada),
- `README.md` proyek diperbarui,
- status di `projects/README.md` diperbarui,
- pengguna bisa menjalankannya sendiri dari instruksi yang ada.
