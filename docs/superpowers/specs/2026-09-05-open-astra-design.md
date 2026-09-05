# Open Astra V1 — Design Spec (2026-09-05)

Goal: open-source Astra-like computer-use agent, Windows-first, community-forkable. V1 = harness + reused brains, no training.

## Architecture
Single loop in `agent.py`, max 20 steps:
screenshot -> planner -> grounder -> executor -> verifier -> repeat

Planner and grounder are interfaces with local + API backends.

## Components
- `perceiver.py`: `mss` screenshot at 1024x768. No a11y tree in V1.
- `planner.py`: `plan(shot, task, history) -> intent` (e.g. click "Search box"). Backends: `ollama` (Qwen3-VL default), `openai`, `anthropic`.
- `grounder.py`: `ground(shot, intent) -> x,y 0-1000`. Default reused OS-Atlas-Base-7B / UGround. No training in V1.
- `executor.py`: Windows `SendInput` via ctypes (primary), pyautogui fallback. Actions: click, double/right, drag, scroll, type, hotkey, wait. Failsafe (0,0), allowlist, approval for writes/deletes.
- `verifier.py`: re-screenshot, `terminate` check, retry on miss (zoomed crop), abort on UAC block.

## Data flow
Task -> [shot, intent, x,y denormalized to px, OS input, new shot]* -> done/fail. Coords always 0-1000 normalized, origin top-left: px = x/1000*width.

## Errors
Grounder miss -> retry with crop. Executor blocked -> abort + log. Planner loop -> max-steps stop. Full action log.

## Testing
One runnable check: `python -m openastra.demo --task "open notepad"` + assert on denormalize math. No OSWorld suite in V1 (V2).

## Repo
Fresh git in OPEN ASTRA/ (isolated from home repo), MIT, pip install -e ., demo.gif. V2: custom grounder training, OSWorld evals, Linux sandbox.
