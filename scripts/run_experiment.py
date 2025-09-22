#!/usr/bin/env python3
import argparse, json, random, time, csv, sys, platform, pathlib, os
from rlshield.sim import run_episode

def load_config(profile:str, path:str):
    if path: return json.load(open(path, "r", encoding="utf-8"))
    here = pathlib.Path(__file__).resolve().parent.parent
    return json.load(open(here / "experiments" / "configs" / (profile + ".json"), "r", encoding="utf-8"))

def ensure_outdir(outdir:str)->pathlib.Path:
    if outdir: d = pathlib.Path(outdir)
    else:
        d = pathlib.Path("results") / f"run_{time.strftime('%Y%m%d_%H%M%S')}"
    d.mkdir(parents=True, exist_ok=True); return d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=["hard","tuned"], default="hard")
    ap.add_argument("--config")
    ap.add_argument("--episodes", type=int, default=None)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--log-steps", action="store_true")
    ap.add_argument("--outdir")
    args = ap.parse_args()

    cfg = load_config(args.profile, args.config)
    if args.episodes is not None: cfg["episodes"] = args.episodes
    episodes = cfg.get("episodes", 20); random.seed(args.seed)
    outdir = ensure_outdir(args.outdir)
    results = []; logf = open(outdir / f"log_{time.strftime('%Y%m%d_%H%M%S')}.jsonl","w",encoding="utf-8") if args.log_steps else None

    for ep in range(episodes):
        r = run_episode(cfg, seed=args.seed + ep, log_steps=args.log_steps); results.append(r)
        if logf:
            for row in r["steps_log"]: logf.write(json.dumps({"episode": ep, **row}) + "\n")
    if logf: logf.close()

    # CSV
    csv_path = outdir / "metrics.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["episode","kept_in_A","t_rec","rho_max","summary_B"])
        w.writeheader()
        for i, r in enumerate(results):
            w.writerow({"episode": i, "kept_in_A": int(r["kept_in_A"]), "t_rec": r["t_rec"], "rho_max": r["rho_max"], "summary_B": r["summary_B"]})

    # Summary
    kept = sum(1 for r in results if r["kept_in_A"]); t_rec_vals = [r["t_rec"] for r in results]
    summary = {
        "episodes": episodes,
        "kept_in_A_frac": kept / episodes if episodes else 0.0,
        "t_rec_median": sorted(t_rec_vals)[len(t_rec_vals)//2],
        "t_rec_95p": sorted(t_rec_vals)[int(0.95*len(t_rec_vals))-1] if episodes>=20 else max(t_rec_vals),
        "rho_max_avg": sum(r["rho_max"] for r in results)/episodes,
        "summary_B_avg": sum(r["summary_B"] for r in results)/episodes,
        "profile": args.profile,
        "config": str(pathlib.Path(args.config).as_posix()) if args.config else f"experiments/configs/{args.profile}.json",
        "seed": args.seed,
        "python": sys.version,
        "platform": platform.platform(),
        "outdir": str(outdir.as_posix())
    }
    json.dump(summary, open(outdir / "summary.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("Wrote:", outdir / "metrics.csv", "and", outdir / "summary.json")

if __name__ == "__main__":
    main()
