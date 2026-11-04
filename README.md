# Dev.Team

**Development Work HQ** — a place where agents, skills, and projects live together for OpenCode.

> Dev.Team — development work headquarters: agent, skills, projects, templates, docs, scripts. For OpenCode.

## What's Inside

| Path | Purpose |
| --- | --- |
| `.opencode/agents/` | Agent definitions (`dev-team.md`) |
| `.opencode/skills/` | Installed skills (`archify`, `unslop`) |
| `projects/` | Active projects + status index |
| `templates/` | New project template (`new-project`) |
| `docs/` | Cross-project notes: design, decisions, diagrams |
| `scripts/` | Helpers: `new-project.sh`, `index-projects.sh` |
| `AGENTS.md` | Main rules — auto-read by agents |
| `README.md` | This guide |

## How to Use

1. Open the **Dev.Team** folder in OpenCode (not subfolders).
2. Pick the **Dev.Team** agent (or call it from the main agent).
3. For specific tasks, load the skill via the `skill` tool with its ID:
   - `archify` — one-page diagrams & explainer
   - `unslop` — clean up AI-looking UI
4. Create a new project:
   ```bash
   ./scripts/new-project.sh <project-name>
   ./scripts/index-projects.sh
   ```

## Skills

| ID | Purpose |
| --- | --- |
| `archify` | Architecture / workflow / sequence / data-flow / lifecycle / ERD / tree / timeline / waterfall + explainer. |
| `unslop` | Clean up UI that looks AI-generated. |

Skills are loaded via the `skill` tool. `AGENTS.md` does not load skills — it only holds context.

## Status

- **Pushed** to GitHub: `ridayz/Dev.Team` (branch `main`)
- Added: 2026-11-04
