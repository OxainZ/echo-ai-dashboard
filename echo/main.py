from __future__ import annotations
import argparse, os
from .engine.echo_engine import EchoEngine
from .engine.reports import format_daily

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", choices=["daily"], default="daily")
    ap.add_argument("--config", default="echo/config.yaml")
    args = ap.parse_args()

    eng = EchoEngine(args.config)
    verdict = eng.run()
    out = format_daily(verdict)

    out_dir = eng.config.get("reporting",{}).get("out_dir","reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "echo_daily.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Report written: {out_path}\n")
    print(out)

if __name__ == "__main__":
    main()
