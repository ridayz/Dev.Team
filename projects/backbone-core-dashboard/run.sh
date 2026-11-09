#!/usr/bin/env bash
# Jalankan Backbone Core Dashboard (Python + SQLite, tanpa Node.js)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER="$ROOT/src/server"

echo "==> Memulai backend di http://localhost:4000"
cd "$SERVER"
python3 app.py &
SERVER_PID=$!

# Tunggu siap
for i in $(seq 1 20); do
  if curl -sf http://localhost:4000/api/health >/dev/null 2>&1; then break; fi
  sleep 0.5
done

echo "==> Buka frontend: file://$ROOT/src/web/index.html"
echo "   Atau gunakan live server (mis. python3 -m http.server 5173 di src/web)"
echo ""
echo "Tekan Ctrl+C untuk menghentikan backend."
wait $SERVER_PID
