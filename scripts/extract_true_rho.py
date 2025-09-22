import glob, os, json, csv, argparse, statistics
ap = argparse.ArgumentParser(); ap.add_argument("--indir"); args = ap.parse_args()
def latest_run_dir():
    runs = sorted(glob.glob("results/run_*"), key=os.path.getmtime)
    return runs[-1] if runs else None
indir = args.indir or latest_run_dir()
if not indir: print("Не знайдено теку результатів."); raise SystemExit(1)
logs = sorted(glob.glob(os.path.join(indir,'log_*.jsonl')), key=os.path.getmtime)
if not logs: print("Логів кроків немає у", indir, " — запускай з --log-steps."); raise SystemExit(1)
by_ep = {}
for line in open(logs[-1],'r',encoding='utf-8'):
    r = json.loads(line); ep = r.get('episode'); 
    if ep is None: continue
    by_ep.setdefault(ep, []).append(r.get('rho', 0))
rows=[{"episode":ep,"rho_max_true":max(series) if series else 0} for ep,series in sorted(by_ep.items())]
out_csv=os.path.join(indir,'rho_true.csv')
with open(out_csv,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=["episode","rho_max_true"]); w.writeheader()
    [w.writerow(r) for r in rows]
avg=statistics.mean(r["rho_max_true"] for r in rows) if rows else 0.0
p95=(sorted(r["rho_max_true"] for r in rows)[int(0.95*len(rows))-1] if len(rows)>=20 else max((r["rho_max_true"] for r in rows), default=0))
print(f"Збережено {out_csv}. Середнє={avg:.2f}, 95-й перцентиль={p95}")
