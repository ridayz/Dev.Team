#!/usr/bin/env bash
# Create a new project from templates/new-project.
# Usage: ./scripts/new-project.sh <project-name>
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/templates/new-project"

if [ $# -ne 1 ]; then
  echo "Usage: $0 <project-name>"
  echo "Example: $0 toko-online"
  exit 1
fi

NAME="$1"

if [ ! -d "$TEMPLATE" ]; then
  echo "Template not found: $TEMPLATE"
  exit 1
fi

if [ -e "$ROOT/projects/$NAME" ]; then
  echo "Project '$NAME' already exists: projects/$NAME"
  exit 1
fi

if ! printf '%s' "$NAME" | grep -qE '^[a-z0-9][a-z0-9-]*$'; then
  echo "Invalid name. Use lowercase letters, numbers, and hyphens."
  echo "Example: toko-online, dashboard-admin"
  exit 1
fi

TODAY="$(date +%F)"
DEST="$ROOT/projects/$NAME"

cp -r "$TEMPLATE" "$DEST"

# Fill name and date in the project README
sed -i "s/^# New Project Template$/# $NAME/" "$DEST/README.md"
sed -i "s/YYYY-MM-DD/$TODAY/g" "$DEST/README.md"

# Create empty marker folders so structure stays visible
for d in src tests docs; do
  [ -d "$DEST/$d" ] || mkdir -p "$DEST/$d"
  touch "$DEST/$d/.gitkeep"
done

"$ROOT/scripts/index-projects.sh" >/dev/null 2>&1 || true

echo "Project created: projects/$NAME"
echo
echo "Next steps:"
echo "  1. Open projects/$NAME/README.md, fill in the Purpose."
echo "  2. Start coding in projects/$NAME/src/"
