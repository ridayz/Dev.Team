#!/usr/bin/env bash
# Regenerasi tabel daftar proyek di projects/README.md.
# Status dibaca dari tiap projects/<nama>/README.md.
# Penggunaan: ./scripts/index-projects.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS="$ROOT/projects"
INDEX="$PROJECTS/README.md"

python3 - "$PROJECTS" "$INDEX" <<'PY'
import os
import re
import sys

projects_dir, index_path = sys.argv[1], sys.argv[2]
rows = []

for name in sorted(os.listdir(projects_dir)):
    path = os.path.join(projects_dir, name)
    readme = os.path.join(path, "README.md")
    if not os.path.isdir(path) or not os.path.isfile(readme):
        continue

    text = open(readme, encoding="utf-8").read()

    status = "rencana"
    m = re.search(r"\|\s*\*\*Status\*\*\s*\|\s*`([^`]+)`", text)
    if m:
        status = m.group(1)

    touched = "—"
    m = re.search(r"\|\s*\*\*Terakhir disentuh\*\*\s*\|\s*([0-9-]{10})", text)
    if m:
        touched = m.group(1)

    rows.append((name, status, touched))

if not rows:
    rows = [("_(belum ada)_", "—", "—")]

table = ["| Proyek | Status | Terakhir disentuh |", "| --- | --- | --- |"]
for name, status, touched in rows:
    cell = f"[{name}]({name}/README.md)" if name != "_(belum ada)_" else name
    table.append(f"| {cell} | `{status}` | {touched} |")

block = "\n".join(table)

start = "<!-- INDEX:START -->"
end = "<!-- INDEX:END -->"

body = (
    "# projects/\n\n"
    "Satu folder = satu proyek. Tidak ada `.opencode/` di dalam sini.\n"
    "Tabel di bawah dibuat otomatis oleh `scripts/index-projects.sh`.\n\n"
    f"{start}\n{block}\n{end}\n\n"
    "## Status yang dipakai\n\n"
    "| Status | Arti |\n| --- | --- |\n"
    "| `rencana` | baru ide, belum ada kode |\n"
    "| `dikerjakan` | sedang aktif |\n"
    "| `review` | kode selesai, sedang dicek |\n"
    "| `selesai` | sudah jalan dan disetujui |\n"
    "| `parkir` | ditunda, bukan dibuang |\n\n"
    "## Membuat proyek baru\n\n"
    "```bash\n./scripts/new-project.sh nama-proyek\n```\n\n"
    "## Aturan\n\n"
    "- Nama folder: huruf kecil, tanda hubung. Contoh: `toko-online`.\n"
    "- Tiap proyek punya `README.md`: tujuan, status, cara menjalankan.\n"
    "- Ubah status di `README.md` proyek, lalu jalankan `./scripts/index-projects.sh`.\n"
    "- Diagram dan catatan lintas proyek disimpan di `docs/` root, bukan di sini.\n"
)

open(index_path, "w", encoding="utf-8").write(body)
print(f"{len(rows)} proyek terindeks")
PY
