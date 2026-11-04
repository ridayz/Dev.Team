#!/usr/bin/env bash
# Buat proyek baru dari templates/new-project.
# Penggunaan: ./scripts/new-project.sh nama-proyek
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/templates/new-project"

if [ $# -ne 1 ]; then
  echo "Penggunaan: $0 nama-proyek"
  echo "Contoh    : $0 toko-online"
  exit 1
fi

NAME="$1"

if [ ! -d "$TEMPLATE" ]; then
  echo "Template tidak ditemukan: $TEMPLATE"
  exit 1
fi

if [ -e "$ROOT/projects/$NAME" ]; then
  echo "Proyek '$NAME' sudah ada: projects/$NAME"
  exit 1
fi

if ! printf '%s' "$NAME" | grep -qE '^[a-z0-9][a-z0-9-]*$'; then
  echo "Nama tidak valid. Pakai huruf kecil, angka, dan tanda hubung."
  echo "Contoh: toko-online, dashboard-admin"
  exit 1
fi

TODAY="$(date +%F)"
DEST="$ROOT/projects/$NAME"

cp -r "$TEMPLATE" "$DEST"

# Isi nama dan tanggal di README proyek
sed -i "s/^# Nama Proyek$/# $NAME/" "$DEST/README.md"
sed -i "s/YYYY-MM-DD/$TODAY/g" "$DEST/README.md"

# Penanda folder kosong supaya struktur tetap terlihat
for d in src tests docs; do
  [ -d "$DEST/$d" ] || mkdir -p "$DEST/$d"
  touch "$DEST/$d/.gitkeep"
done

"$ROOT/scripts/index-projects.sh" >/dev/null 2>&1 || true

echo "Proyek dibuat: projects/$NAME"
echo
echo "Langkah berikutnya:"
echo "  1. Buka projects/$NAME/README.md, isi Tujuan."
echo "  2. Mulai kode di projects/$NAME/src/"
