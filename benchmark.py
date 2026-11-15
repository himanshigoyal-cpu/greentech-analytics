"""Usage: python benchmark.py <url> <label> [--token T] [--levels 1,5,10,25,50]
Fires concurrent GETs at each level, prints a markdown table (avg/p95 latency, errors, req/s)."""
import argparse, statistics, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("url"); ap.add_argument("label")
ap.add_argument("--token"); ap.add_argument("--levels", default="1,5,10,25,50")
a = ap.parse_args()


def hit(_):
    req = urllib.request.Request(a.url)
    if a.token:
        req.add_header("Authorization", f"Bearer {a.token}")
    t = time.perf_counter()
    try:
        urllib.request.urlopen(req, timeout=30).read()
        return (time.perf_counter() - t) * 1000, True
    except Exception:
        return (time.perf_counter() - t) * 1000, False


print(f"| {a.label} concurrency | avg ms | p95 ms | errors | req/s |\n|---|---|---|---|---|")
hit(0)  # warm-up (note the cold start separately!)
for n in map(int, a.levels.split(",")):
    s = time.perf_counter()
    with ThreadPoolExecutor(n) as ex:
        res = list(ex.map(hit, range(n * 4)))
    wall = time.perf_counter() - s
    lat = sorted(r[0] for r in res)
    print(f"| {n} | {statistics.mean(lat):.0f} | {lat[int(len(lat)*.95)-1]:.0f} | "
          f"{sum(not r[1] for r in res)} | {len(res)/wall:.1f} |")
