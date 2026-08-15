import os, glob, json, psutil, sys
me = os.getpid()
print("diag pid:", me)
# Replicate ocr_running and report matches
OCR_PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_running_pid.txt")
print("pid file exists:", os.path.exists(OCR_PID_FILE), "content:", repr(open(OCR_PID_FILE).read() if os.path.exists(OCR_PID_FILE) else ""))

print("=== ALL python processes ===")
for p in psutil.process_iter(["pid","cmdline","create_time"]):
    cl = p.info.get("cmdline") or []
    if any("python" in (c or "").lower() for c in cl):
        print(p.pid, "::", " ".join(cl)[:200])

print("=== /proc matches for 'ocr_all' ===")
for cf in glob.glob("/proc/[0-9]*/cmdline"):
    try:
        c = open(cf,"rb").read().replace(b"\x00",b" ").decode("utf-8","ignore")
        if "ocr_all" in c:
            pid = cf.split("/")[2]
            print(pid, "::", c[:200])
    except Exception:
        pass

print("=== psutil matches for 'ocr_all' ===")
for p in psutil.process_iter(["pid","cmdline"]):
    cl = " ".join(p.info.get("cmdline") or [])
    if "ocr_all" in cl:
        print(p.pid, "::", cl[:200])
print("=== done ===")
