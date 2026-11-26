"""Unit tests for helper/deskmate_stats.py parsers, using real-format macOS command output.
Run: python3 tests/test_helper.py"""
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('ds', pathlib.Path(__file__).resolve().parent.parent / 'helper' / 'deskmate_stats.py')
ds = importlib.util.module_from_spec(spec); spec.loader.exec_module(ds)

TOP = "CPU usage: 7.31% user, 5.12% sys, 87.56% idle "
VM_STAT = """Mach Virtual Memory Statistics: (page size of 16384 bytes)
Pages free:                                3466.
Pages active:                            300000.
Pages inactive:                          290000.
Pages speculative:                         5000.
Pages throttled:                              0.
Pages wired down:                        150000.
Pages purgeable:                          10000.
"Translation faults":                 123456789.
Pages occupied by compressor:            100000.
"""
NETSTAT = """Name       Mtu   Network       Address            Ipkts Ierrs     Ibytes    Opkts Oerrs     Obytes  Coll
lo0        16384 <Link#1>                        561839     0  105912384   561839     0  105912384     0
lo0        16384 127           127.0.0.1         561839     -  105912384   561839     -  105912384     -
gif0*      1280  <Link#2>                             0     0          0        0     0          0     0
en0        1500  <Link#11>   a4:83:e7:12:34:56  9876543     0 12345678901  4567890     0  987654321     0
en0        1500  fe80::1c3a:  fe80:b::1c3a:1d1  9876543     - 12345678901  4567890     - 987654321     -
en0        1500  192.168.1     192.168.1.23      9876543     - 12345678901  4567890     - 987654321     -
utun0      1380  <Link#15>                           10     0       2000       12     0       3000     0
awdl0      1500  <Link#13>   1a:2b:3c:4d:5e:6f       50     0       9000       60     0       8000     0
en1        1500  <Link#7>    82:11:22:33:44:55     1000     0     500000      900     0     400000     0
"""
TOTAL = 16 * 1024 ** 3   # a 16 GB Mac

ok = True
def check(name, got, want):
    global ok
    good = got == want
    ok &= good
    print(('PASS' if good else 'FAIL'), name, got, '' if good else f'(expected {want})')

check('top cpu %', ds.parse_top_cpu(TOP), 12.4)
avail, total = ds.parse_vm_stat(VM_STAT, TOTAL)
used_mb = (300000 + 150000 + 100000) * 16384 / 1048576     # active + wired + compressed
check('vm_stat total MB', total, 16384.0)
check('vm_stat available MB', avail, round(16384 - used_mb, 1))
check('netstat totals (en0 + en1 Link rows only, no loopback/utun/awdl)', ds.parse_netstat_ib(NETSTAT), (12345678901 + 500000, 987654321 + 400000))
check('linux /proc/stat', ds.parse_proc_stat('cpu  100 0 50 800 50 0 0 0 0 0\ncpu0 1 2 3 4\n'), (850, 1000))
check('linux meminfo', ds.parse_meminfo('MemTotal:       16384000 kB\nMemFree:  100 kB\nMemAvailable:    8192000 kB\n'), (8000.0, 16000.0))
check('linux net/dev', ds.parse_proc_net_dev('Inter-|\n face |\n    lo: 999 1 0 0 0 0 0 0 999 1 0 0 0 0 0 0\n  eth0: 5000 10 0 0 0 0 0 0 3000 8 0 0 0 0 0 0\n'), (5000, 3000))
print('ALL PASS' if ok else 'SOME FAILED')
