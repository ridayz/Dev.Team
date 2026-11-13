# Native launcher

Builds the double-click `.exe` for each local dashboard. One C# source, compiled
twice, no Visual Studio, no NuGet, no installer.

## Build

```bat
scripts\native-launcher\build.cmd
```

Output (one file per app, each with its own icon):

| File | App | Port |
| --- | --- | --- |
| `projects\free-model-radar\Free Model Radar.exe` | Free Model Radar | 4173 |
| `projects\dark-fiber-core-manager\Dark Fiber Manager.exe` | Dark Fiber Core Manager | 4174 |

Both `.exe` files are gitignored: they are build output, and `build.cmd` can
regenerate them from `Launcher.cs` at any time.

## What double-click does

1. If the server is already listening on its port, it only opens the browser.
2. Otherwise it starts the server **hidden** (no console window), waits up to 45
   seconds for the port to answer, then opens the default browser.
3. A tray icon appears: double-click to reopen the dashboard, or use the menu to
   stop the server and quit.
4. Launching the `.exe` again while it runs just reopens the browser; a named
   mutex keeps one tray icon per app.

Server output goes to `%LOCALAPPDATA%\Dev.Team\logs\server-<port>.log`.

The tray menu has two different exits:

- **Hentikan server & keluar** — kills the server, then the launcher.
- **Tutup ikon (server tetap jalan)** — hides the tray, server keeps serving; the
  next double-click attaches to it and can still stop it (the launcher finds the
  process that owns the port).

## Runtime detection

| App | Runtime | Lookup order |
| --- | --- | --- |
| Free Model Radar | `node.exe` | `C:\Program Files\nodejs\node.exe`, then `PATH` |
| Dark Fiber | `pythonw.exe` | `D:\tools\python312\pythonw.exe`, then `python.exe`, then `PATH` |

`PORT` and `PYTHONIOENCODING=utf-8` are set for the child process, so both
servers behave the same as when started from a terminal.

## Icons

`icons\*.ico` are prebuilt multi-size (16/32/48/64/128/256) icons. To change one:

1. Edit the SVG (`icons\dark-fiber-core-manager.svg`) or the app's `favicon.svg`.
2. Rasterise and pack into `.ico` with Playwright + Chrome (script kept in
   `D:\tmp\fmr-shot\make-icons.mjs`, not committed because it needs
   `playwright-core`).
3. Rebuild with `build.cmd`.

## Shortcuts

Desktop shortcuts point at these `.exe` files. If a project folder moves, update
the shortcut target.
