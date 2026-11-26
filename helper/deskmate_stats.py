#!/usr/bin/env python3
"""Deskmate stats helper: real PC metrics for the wallpaper on macOS (and Linux).

Windows already gets these from Lively Wallpaper. On a Mac, Plash shows the wallpaper as a web page,
and web pages can't read hardware stats, so this tiny program reads them and hands them to the
wallpaper over a local-only connection:

    http://127.0.0.1:47800/stats   ->  {"CurrentCpu": 23.4, "CurrentRamAvail": 9123, ...}

- Uses only Python's standard library and tools built into macOS (top, vm_stat, sysctl, netstat).
- Listens on 127.0.0.1 only, so other computers can't reach it. It answers only local wallpaper
  files (Origin "null"), never websites.
- Read-only: it never changes anything on the computer.

Run:  python3 deskmate_stats.py        (or install it to start at login: ./install-mac.sh)
"""
import json, os, platform, re, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = '127.0.0.1', int(os.environ.get('DESKMATE_STATS_PORT', '47800'))
STATE = {'cpu': None, 'net': (0.0, 0.0), 'names': {}}
LOCK = threading.Lock()


def run(cmd, timeout=10):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except Exception:
        return ''


# ---------------------------------------------------------------- parsers (pure, unit-tested) ----
def parse_top_cpu(line):
    """'CPU usage: 7.31% user, 5.12% sys, 87.56% idle' -> 12.44"""
    m = re.search(r'([\d.]+)%\s*idle', line)
    return round(100 - float(m.group(1)), 1) if m else None


def parse_vm_stat(text, total_bytes):
    """macOS vm_stat -> (available_MB, total_MB). 'Used' = active + wired + compressed (like Activity Monitor's 'Memory Used')."""
    page = int((re.search(r'page size of (\d+) bytes', text) or [0, 16384])[1])
    def pages(label):
        m = re.search(r'^' + re.escape(label) + r':\s+(\d+)', text, re.M)
        return int(m.group(1)) if m else 0
    used = (pages('Pages active') + pages('Pages wired down') + pages('Pages occupied by compressor')) * page
    total_mb = total_bytes / 1048576
    return round(max(0.0, total_mb - used / 1048576), 1), round(total_mb, 1)


def parse_netstat_ib(text):
    """macOS `netstat -ibn` -> total (bytes_in, bytes_out) over real interfaces (no loopback), counted once per interface."""
    lines = text.strip().splitlines()
    if not lines:
        return 0, 0
    head = lines[0].split()
    try:
        i_in, i_out = head.index('Ibytes'), head.index('Obytes')
    except ValueError:
        return 0, 0
    seen, rx, tx = set(), 0, 0
    for ln in lines[1:]:
        cols = ln.split()
        if len(cols) < len(head) or not cols[0] or cols[0].startswith(('lo', 'gif', 'stf', 'utun', 'awdl', 'llw', 'bridge', 'anpi', 'ap')):
            continue
        if '<Link#' not in ln or cols[0] in seen:     # the <Link#n> row holds the interface's totals
            continue
        seen.add(cols[0])
        # rows can miss the Address column; read counters from the right-hand end
        off = len(cols) - len(head)
        try:
            rx += int(cols[i_in + off]); tx += int(cols[i_out + off])
        except (ValueError, IndexError):
            pass
    return rx, tx


def parse_proc_stat(text):
    """Linux /proc/stat first line -> (idle, total) jiffies."""
    vals = [int(v) for v in text.splitlines()[0].split()[1:]]
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
    return idle, sum(vals)


def parse_meminfo(text):
    """Linux /proc/meminfo -> (available_MB, total_MB)."""
    kb = {k: int(v) for k, v in re.findall(r'^(\w+):\s+(\d+)', text, re.M)}
    return round(kb.get('MemAvailable', kb.get('MemFree', 0)) / 1024, 1), round(kb.get('MemTotal', 0) / 1024, 1)


def parse_proc_net_dev(text):
    """Linux /proc/net/dev -> total (bytes_in, bytes_out), loopback excluded."""
    rx = tx = 0
    for ln in text.splitlines()[2:]:
        name, _, data = ln.partition(':')
        if name.strip() == 'lo' or not data:
            continue
        f = data.split()
        rx += int(f[0]); tx += int(f[8])
    return rx, tx


# ---------------------------------------------------------------- live readers ----
MAC = sys.platform == 'darwin'


def cpu_loop():
    """CPU %: on macOS a single long-running `top` (one sample every 2 s); on Linux /proc/stat deltas."""
    if MAC:
        while True:
            try:
                p = subprocess.Popen(['top', '-l', '0', '-s', '2', '-n', '0'], stdout=subprocess.PIPE, text=True)
                first = True
                for line in p.stdout:
                    if line.startswith('CPU usage'):
                        if first:            # top's very first sample is an average since boot — skip it
                            first = False
                            continue
                        with LOCK:
                            STATE['cpu'] = parse_top_cpu(line)
            except Exception:
                pass
            time.sleep(5)
    else:
        prev = None
        while True:
            try:
                cur = parse_proc_stat(open('/proc/stat').read())
                if prev:
                    di, dt = cur[0] - prev[0], cur[1] - prev[1]
                    with LOCK:
                        STATE['cpu'] = round(100 * (1 - di / dt), 1) if dt else 0.0
                prev = cur
            except Exception:
                pass
            time.sleep(1)


def net_totals():
    if MAC:
        return parse_netstat_ib(run(['netstat', '-ibn']))
    try:
        return parse_proc_net_dev(open('/proc/net/dev').read())
    except Exception:
        return 0, 0


def net_loop():
    prev, pt = net_totals(), time.time()
    while True:
        time.sleep(1)
        cur, ct = net_totals(), time.time()
        dt = max(ct - pt, 1e-3)
        down, up = max(0, cur[0] - prev[0]) / dt, max(0, cur[1] - prev[1]) / dt
        with LOCK:
            STATE['net'] = (round(down), round(up))
        prev, pt = cur, ct


def memory():
    if MAC:
        total = int(run(['sysctl', '-n', 'hw.memsize']).strip() or 0)
        return parse_vm_stat(run(['vm_stat']), total)
    try:
        return parse_meminfo(open('/proc/meminfo').read())
    except Exception:
        return 0.0, 0.0


def names():
    """Chip / GPU / network names, read once at start."""
    out = {'NameCpu': '', 'NameGpu': '', 'NameNetCard': ''}
    if MAC:
        out['NameCpu'] = run(['sysctl', '-n', 'machdep.cpu.brand_string']).strip()
        gpu = re.findall(r'Chipset Model:\s*(.+)', run(['system_profiler', 'SPDisplaysDataType'], timeout=20))
        out['NameGpu'] = gpu[0].strip() if gpu else ''
        iface = (re.search(r'interface:\s*(\S+)', run(['route', '-n', 'get', 'default'])) or [None, ''])[1]
        ports = run(['networksetup', '-listallhardwareports'])
        m = re.search(r'Hardware Port:\s*(.+)\nDevice:\s*' + re.escape(iface) + r'\b', ports) if iface else None
        out['NameNetCard'] = (m.group(1).strip() + f' ({iface})') if m else iface
    else:
        try:
            out['NameCpu'] = (re.search(r'^model name\s*:\s*(.+)$', open('/proc/cpuinfo').read(), re.M) or [None, platform.processor()])[1].strip()
        except Exception:
            out['NameCpu'] = platform.processor()
    return out


def snapshot():
    avail, total = memory()
    with LOCK:
        cpu, (down, up), nm = STATE['cpu'], STATE['net'], dict(STATE['names'])
    return {**nm, 'CurrentCpu': cpu if cpu is not None else 0, 'CurrentGpu3D': None,   # macOS doesn't share GPU % without admin rights
            'CurrentRamAvail': avail, 'TotalRam': total, 'CurrentNetDown': down, 'CurrentNetUp': up,
            'Source': 'deskmate-stats'}


# ---------------------------------------------------------------- local-only web server ----
class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        # Only local wallpaper files (file:// pages send Origin "null") may read the stats — not websites.
        if self.headers.get('Origin') == 'null':
            self.send_header('Access-Control-Allow-Origin', 'null')
            self.send_header('Access-Control-Allow-Private-Network', 'true')
            self.send_header('Vary', 'Origin')

    def do_OPTIONS(self):
        self.send_response(204); self._cors()
        self.send_header('Access-Control-Allow-Methods', 'GET'); self.end_headers()

    def do_GET(self):
        if self.path.split('?')[0] != '/stats':
            self.send_response(404); self.end_headers(); return
        body = json.dumps(snapshot()).encode()
        self.send_response(200); self._cors()
        self.send_header('Content-Type', 'application/json'); self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)

    def log_message(self, *a):   # stay quiet
        pass


def main():
    STATE['names'] = names()
    for fn in (cpu_loop, net_loop):
        threading.Thread(target=fn, daemon=True).start()
    try:
        srv = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as e:
        print(f'deskmate-stats: port {PORT} is busy ({e}). Is it already running?'); sys.exit(1)
    print(f'deskmate-stats: serving on http://{HOST}:{PORT}/stats  (Ctrl+C to stop)')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
