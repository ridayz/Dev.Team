# AGENTS.md — Dev.Team Rules

This file is auto-read by every agent in this folder. It holds the main rules, not documentation. If unsure, follow this file.

## Workspace Map

```
Dev.Team/
├── AGENTS.md              ← here (rules)
├── README.md              ← human guide
├── .opencode/
│   ├── agents/            ← agent definitions
│   └── skills/            ← skills (archify, unslop, ...)
├── projects/              ← all projects
│   ├── README.md          ← index + status
│   └── <project-name>/
│       ├── README.md      ← purpose, status, how to run
│       ├── src/           ← code
│       ├── tests/         ← tests
│       └── docs/          ← project-specific notes
├── templates/new-project/ ← new project template
├── docs/
│   ├── decisions/         ← why a decision was made
│   ├── diagrams/          ← archify results
│   └── notes/             ← cross-project notes
└── scripts/               ← helpers (new-project.sh)
```

## File Placement Rules

| File type | Put in | Don't put in |
| --- | --- | --- |
| App code | `projects/<project>/src/` | repo root |
| Tests | `projects/<project>/tests/` | `src/` |
| Project notes | `projects/<project>/docs/` | root `docs/` |
| Diagrams (archify) | `docs/diagrams/` | inside project |
| Architecture decisions | `docs/decisions/` | project README |
| Helper scripts | `scripts/` | `src/` |
| New skill | `.opencode/skills/<id>/SKILL.md` | inside project |

## Hard Rules

1. **Do not create `.opencode/` inside `projects/*/`.** One `.opencode` at root already applies to all.
2. **Do not change `.opencode/skills/`** unless installing or replacing a skill.
3. **Do not delete existing projects.** Mark them `done` or `paused` in the index.
4. **Do not put secrets** (`.env`, token, password) in the repo. Use `.env.example`.
5. **Do not put large files** (ISO, zip, video) in the HQ. Store outside.

## Expected Workflow

1. Read `projects/README.md` first for context.
2. Read the README of the project being touched.
3. If the work is more than 3 steps, write a short plan first.
4. Work in parts, verify each part.
5. Update status in `projects/README.md` after done.

## Naming Conventions

| Item | Format | Example |
| --- | --- | --- |
| Project folder | lowercase, hyphenated | `toko-online` |
| Code file | per language | `checkout.ts` |
| Note | `kebab-case.md` | `rencana-checkout.md` |
| Decision | `NNNN-title.md` | `0001-use-postgres.md` |
| Diagram | `<project>-<type>.html` | `toko-online-architecture.html` |

## Project Statuses

`idea` → `in-progress` → `review` → `done` / `paused`

## Skills

- Skills are loaded via the `skill` tool with the ID (folder name, case-sensitive).
- `AGENTS.md` does not load skills. It only holds context.
- New skill: put it in `.opencode/skills/<id>/SKILL.md`, then register it in `dev-team.md`.
- Load only when relevant. If the user mentions a skill, load it before starting.

## Done Definition

A task is done when:
- Code runs without error,
- tests/lint pass (if any),
- project `README.md` updated,
- status in `projects/README.md` updated,
- user can run it themselves from the instructions.
