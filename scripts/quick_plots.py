import csv, json, glob, os, argparse
import matplotlib.pyplot as plt
ap = argparse.ArgumentParser(); ap.add_argument("--indir"); args = ap.parse_args()
def latest_run_dir():
    runs = sorted(glob.glob("results/run_*"), key=os.path.getmtime)
    return runs[-1] if runs else None
indir = args.indir or latest_run_dir()
if not indir or not os.path.exists(os.path.join(indir,"metrics.csv")):
    print("Не знайдено результати. Вкажи --indir або запусти експеримент."); raise SystemExit(1)
vals=[]; 
import csv as _csv
with open(os.path.join(indir,'metrics.csv'), newline='', encoding='utf-8') as f:
    for row in _csv.DictReader(f): vals.append(int(row['t_rec']))
plt.hist(vals, bins=15); plt.xlabel('T_rec (кроки)'); plt.ylabel('кількість епізодів'); plt.title('Розподіл часу відновлення')
plt.savefig(os.path.join(indir,'t_rec_hist.png'), dpi=150); plt.close()
logs = sorted(glob.glob(os.path.join(indir,'log_*.jsonl')), key=os.path.getmtime)
if logs:
    recs = [json.loads(line) for line in open(logs[-1], 'r', encoding='utf-8')]
    ep0 = [r for r in recs if r.get('episode')==0]
    if ep0:
        ts=[r['t'] for r in ep0]; Bs=[r['B'] for r in ep0]
        plt.plot(ts, Bs); plt.xlabel('t'); plt.ylabel('B(t)'); plt.title('Бар’єр за часом (епізод 0)')
        plt.savefig(os.path.join(indir,'episode0_B.png'), dpi=150); plt.close()
print("OK:", indir)
