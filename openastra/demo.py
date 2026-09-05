import argparse
from openastra.agent import run

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--max-steps", type=int, default=20)
    ap.add_argument("--planner", choices=["stub", "ollama"], default="stub")
    ap.add_argument("--grounder", choices=["center", "ollama"], default="center")
    ap.add_argument("--model", default="qwen2.5vl:3b")
    a = ap.parse_args()
    print(run(a.task, max_steps=a.max_steps, dry_run=a.dry_run, planner=a.planner, grounder=a.grounder, model=a.model))
