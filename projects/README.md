# projects/

Satu folder = satu proyek. Tidak ada `.opencode/` di dalam sini.
Tabel di bawah dibuat otomatis oleh `scripts/index-projects.sh`.

<!-- INDEX:START -->
| Proyek | Status | Terakhir disentuh |
| --- | --- | --- |
| _(belum ada)_ | `—` | — |
<!-- INDEX:END -->

## Status yang dipakai

| Status | Arti |
| --- | --- |
| `rencana` | baru ide, belum ada kode |
| `dikerjakan` | sedang aktif |
| `review` | kode selesai, sedang dicek |
| `selesai` | sudah jalan dan disetujui |
| `parkir` | ditunda, bukan dibuang |

## Membuat proyek baru

```bash
./scripts/new-project.sh nama-proyek
```

## Aturan

- Nama folder: huruf kecil, tanda hubung. Contoh: `toko-online`.
- Tiap proyek punya `README.md`: tujuan, status, cara menjalankan.
- Ubah status di `README.md` proyek, lalu jalankan `./scripts/index-projects.sh`.
- Diagram dan catatan lintas proyek disimpan di `docs/` root, bukan di sini.
