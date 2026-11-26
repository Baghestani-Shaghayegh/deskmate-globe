# Stats helper (macOS / Linux)

Shows **real PC metrics** in the wallpaper's SYSTEM panel when you're not on Windows + Lively.

A wallpaper is a web page, and web pages can't read hardware stats. This tiny program reads them and hands them
to the wallpaper over a connection that only exists inside your own computer (`http://127.0.0.1:47800/stats`).

| | macOS | Linux |
|---|---|---|
| CPU % | ✅ | ✅ |
| Memory used / total | ✅ | ✅ |
| Network down / up | ✅ | ✅ |
| Chip and network names | ✅ | CPU only |
| GPU % | ❌ macOS only shares it with admin rights, so the row is hidden | ❌ |

## Install on a Mac (starts by itself at login)
1. Open **Terminal** and go to this folder, e.g. `cd ~/Downloads/deskmate-globe/helper`.
2. Run:
   ```bash
   bash install-mac.sh
   ```
   The first time, macOS may offer to install the **Command Line Tools** (they include Python). Click **Install**, wait, then run the command again.
3. Reload the wallpaper (Plash → **Reload**). The **SYSTEM** panel appears with live numbers.

To remove it: `bash uninstall-mac.sh`

## Run it by hand (any Mac / Linux)
```bash
python3 deskmate_stats.py
```
Leave the window open. Press Ctrl+C to stop.

## Safety
- **Local only:** it listens on `127.0.0.1`, so other computers on your network can't reach it.
- **Only your wallpaper can read it:** it gives permission to local files only, never to websites.
- **Read-only:** it never changes anything. It only uses built-in tools (`top`, `vm_stat`, `sysctl`, `netstat`), with no downloads and no extra packages.
