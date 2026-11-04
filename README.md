# Dev.Team

Markas kerja pengembangan. Semua proyek dikerjakan dari sini.

```
Dev.Team/
├── AGENTS.md              ← aturan main, dibaca otomatis agent
├── README.md              ← panduan untuk manusia
├── .opencode/
│   ├── agents/            ← definisi agent
│   └── skills/            ← skill (archify, unslop, ...)
├── projects/              ← proyek aktif + selesai (dengan status)
├── templates/             ← cetakan proyek baru
├── docs/                  ← diagram, keputusan, catatan lintas
├── scripts/               ← helper
└── .gitignore
```

## Cara pakai

1. Buka folder **Dev.Team** di OpenCode.
2. Pilih agent **Dev.Team** (atau panggil dari agent utama).
3. Perintah umum:

```bash
./scripts/new-project.sh nama-proyek   # buat proyek baru dari template
./scripts/index-projects.sh           # perbarui indeks proyek
```

## Skill

Diisi lewat tool `skill` dengan ID (nama folder, case-sensitive):

| ID | Kegunaan |
| --- | --- |
| `archify` | Diagram arsitektur/workflow/sequence/data-flow/lifecycle/ERD/tree/timeline/waterfall sebagai HTML interaktif, plus explainer satu halaman. |
| `unslop` | Merapikan UI yang terlihat "AI-generated". |

Muat hanya saat relevan. Jika pengguna menyebut skill, muat dulu sebelum mulai.

## Membuat proyek

```bash
./scripts/new-project.sh toko-online
# edit projects/toko-online/README.md
# kerjakan di projects/toko-online/src/
# update status + ./scripts/index-projects.sh
```

## Menambah skill baru

1. Ambil dari GitHub: repo → tarball → `.opencode/skills/<id>/SKILL.md`.
2. Tambahkan ke tabel di `dev-team.md`.
3. Jangan taruh di dalam `projects/*/` — harus di root markas.

## Aturan penting

- Jangan buat `.opencode/` di dalam `projects/*/`.
- Jangan ubah `.opencode/skills/` kecuali memasang/mengganti.
- Jangan hapus proyek yang sudah ada; tandai `selesai` / `parkir`.
- Jangan taruh rahasia / file besar di markas.

Lihat `AGENTS.md` untuk aturan lengkap.
