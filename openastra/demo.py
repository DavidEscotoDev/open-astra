import argparse
from openastra.agent import run

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--max-steps", type=int, default=20)
    a = ap.parse_args()
    print(run(a.task, max_steps=a.max_steps, dry_run=a.dry_run))
