# Dev.Team

**Markas kerja pengembangan** — tempat agent, skills, dan proyek dikumpulkan dalam satu tempat untuk OpenCode.

> `Dev.Team — markas kerja: agent, skills, proyek, templates, docs, scripts. Untuk OpenCode.`

## Apa isi repo

| Folder / File | Isi |
| --- | --- |
| `.opencode/agents/` | Definisi agent (`dev-team.md`) |
| `.opencode/skills/` | Skill terpasang (`archify`, `unslop`) |
| `projects/` | Proyek aktif + status (dengan tabel indeks) |
| `templates/` | Cetakan proyek baru (`new-project`) |
| `docs/` | Catatan lintas proyek: desain, keputusan, diagram |
| `scripts/` | Helper: `new-project.sh`, `index-projects.sh` |
| `AGENTS.md` | Aturan main — dibaca otomatis agent |
| `README.md` | Panduan ini |

## Cara pakai

1. Buka folder **Dev.Team** di OpenCode (bukan subfolder-nya).
2. Pilih agent **Dev.Team** (atau panggil dari agent utama).
3. Untuk task spesifik, panggil skill lewat tool `skill` dengan ID-nya:
   - `archify` — diagram & explainer satu halaman
   - `unslop` — rapikan UI yang kelihatan AI-generated
4. Buat proyek baru:
   ```bash
   ./scripts/new-project.sh nama-proyek
   ./scripts/index-projects.sh
   ```

## Skill

| ID | Kegunaan |
| --- | --- |
| `archify` | Diagram arsitektur/workflow/sequence/data-flow/lifecycle/ERD/tree/timeline/waterfall + explainer satu halaman. |
| `unslop` | Merapikan UI yang terlihat "AI-generated". |

Skill di-load lewat tool `skill`. AGENTS.md tidak me-load skill — AGENTS.md hanya instruksi konteks.

## Status

- **ter-push** ke GitHub: `ridayz/Dev.Team` (branch `main`)
- Ditambahkan: 2026-11-04
