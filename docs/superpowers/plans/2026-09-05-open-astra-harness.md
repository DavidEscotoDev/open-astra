# Open Astra Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Working Windows screenshot-to-click loop with pluggable local/API brains.

**Architecture:** `agent.py` loop calls planner (intent) -> grounder (x,y 0-1000) -> executor (SendInput) -> verifier (re-shot). Coords module shared. No training, no a11y tree.

**Tech Stack:** Python 3.11, mss, pyautogui, ollama (Qwen3-VL), pytest

## Global Constraints
- Windows-first via ctypes SendInput primary, pyautogui fallback
- Coords always 0-1000 normalized, origin top-left, px = int(x/1000*width)
- Max 20 steps per task, full action log
- Failsafe mouse to (0,0) aborts, approval required for writes/deletes
- MIT, pip install -e ., fresh git in OPEN ASTRA/

---

### Task 1: Scaffolding + coords

**Files:**
- Create: `pyproject.toml`
- Create: `openastra/__init__.py`
- Create: `openastra/coords.py`
- Test: `tests/test_coords.py`

**Interfaces:**
- Consumes: none
- Produces: `coords.denormalize(x1000: int, y1000: int, w: int, h: int) -> tuple[int,int]`, `coords.clamp1000(v: int) -> int`

- [ ] **Step 1: Write the failing test**

```python
from openastra.coords import denormalize, clamp1000

def test_denormalize_center():
    assert denormalize(500, 500, 1920, 1080) == (960, 540)

def test_denormalize_clamps():
    assert denormalize(1500, -50, 1000, 1000) == (1000, 0)

def test_clamp1000():
    assert clamp1000(1500) == 1000
    assert clamp1000(-5) == 0
    assert clamp1000(512) == 512
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_coords.py -v`
Expected: FAIL with "No module named 'openastra'"

- [ ] **Step 3: Write minimal implementation**

```python
def clamp1000(v: int) -> int:
    return max(0, min(1000, int(v)))

def denormalize(x1000: int, y1000: int, w: int, h: int) -> tuple[int, int]:
    return (int(clamp1000(x1000) / 1000 * w), int(clamp1000(y1000) / 1000 * h))
```

`pyproject.toml`:
```toml
[project]
name = "openastra"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["mss", "pyautogui", "pytest"]
[tool.pytest.ini_options]
testpaths = ["tests"]
```

`openastra/__init__.py`: empty.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_coords.py -v`
Expected: PASS 3 passed

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml openastra/__init__.py openastra/coords.py tests/test_coords.py
git commit -m "feat: add coords denormalize + clamp"
```

### Task 2: Perceiver (screenshot)

**Files:**
- Create: `openastra/perceiver.py`
- Test: `tests/test_perceiver.py`

**Interfaces:**
- Consumes: none
- Produces: `perceiver.screenshot() -> tuple[bytes, int, int]` returns (png_bytes, width, height)

- [ ] **Step 1: Write the failing test**

```python
from openastra.perceiver import screenshot

def test_screenshot_returns_png_and_size():
    png, w, h = screenshot()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert w > 0 and h > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_perceiver.py -v`
Expected: FAIL with "No module named" or "cannot import screenshot"

- [ ] **Step 3: Write minimal implementation**

```python
import mss
from mss.tools import to_png

def screenshot() -> tuple[bytes, int, int]:
    with mss.mss() as sct:
        mon = sct.monitors[1]
        shot = sct.grab(mon)
        return (to_png(shot.rgb, shot.size), shot.width, shot.height)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_perceiver.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add openastra/perceiver.py tests/test_perceiver.py
git commit -m "feat: add mss screenshot perceiver"
```

### Task 3: Planner interface (ollama + stub)

**Files:**
- Create: `openastra/planner.py`
- Test: `tests/test_planner.py`

**Interfaces:**
- Consumes: screenshot bytes from Task 2 (opaque, passed as bytes)
- Produces: `planner.StubPlanner.plan(shot: bytes, task: str, history: list) -> dict` returns `{"action": "click"|"type"|"done", "target": str, "text": str}`

- [ ] **Step 1: Write the failing test**

```python
from openastra.planner import StubPlanner

def test_stub_planner_click():
    p = StubPlanner()
    out = p.plan(b"fake-png", "open notepad", [])
    assert out["action"] in ("click", "type", "done")
    assert "target" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_planner.py -v`
Expected: FAIL with "cannot import StubPlanner"

- [ ] **Step 3: Write minimal implementation**

```python
import json
import urllib.request

class StubPlanner:
    def plan(self, shot: bytes, task: str, history: list) -> dict:
        return {"action": "click", "target": task, "text": ""}

class OllamaPlanner:
    def __init__(self, model: str = "qwen3-vl"):
        self.model = model

    def plan(self, shot: bytes, task: str, history: list) -> dict:
        import base64
        b64 = base64.b64encode(shot).decode()
        payload = json.dumps({
            "model": self.model, "stream": False,
            "messages": [{"role": "user",
                "content": f"Task: {task}. History: {history}. Reply JSON only: {{\"action\": \"click|type|done\", \"target\": \"...\", \"text\": \"...\"}}",
                "images": [b64]}]}).encode()
        req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
        return json.loads(data["message"]["content"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_planner.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add openastra/planner.py tests/test_planner.py
git commit -m "feat: add stub + ollama planner"
```

### Task 4: Grounder interface (stub, OS-Atlas hook)

**Files:**
- Create: `openastra/grounder.py`
- Test: `tests/test_grounder.py`

**Interfaces:**
- Consumes: `planner` intent dict `{"action":..., "target": str}`
- Produces: `grounder.CenterGrounder.ground(shot: bytes, w: int, h: int, target: str) -> tuple[int,int]` returns (x1000, y1000)

- [ ] **Step 1: Write the failing test**

```python
from openastra.grounder import CenterGrounder

def test_center_grounder():
    g = CenterGrounder()
    assert g.ground(b"png", 1920, 1080, "Search box") == (500, 500)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_grounder.py -v`
Expected: FAIL with "cannot import CenterGrounder"

- [ ] **Step 3: Write minimal implementation**

```python
class CenterGrounder:
    def ground(self, shot: bytes, w: int, h: int, target: str) -> tuple[int, int]:
        return (500, 500)
# ponytail: center stub, swap with OS-Atlas/UGround HTTP when accuracy matters
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_grounder.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add openastra/grounder.py tests/test_grounder.py
git commit -m "feat: add center grounder stub"
```

### Task 5: Executor (Windows click)

**Files:**
- Create: `openastra/executor.py`
- Test: `tests/test_executor.py`

**Interfaces:**
- Consumes: `coords.denormalize` from Task 1
- Produces: `executor.click_px(x: int, y: int, dry_run: bool = True) -> tuple[int,int]`, `executor.type_text(text: str, dry_run: bool = True) -> str`

- [ ] **Step 1: Write the failing test**

```python
from openastra.executor import click_px, type_text

def test_click_dry_run():
    assert click_px(100, 200, dry_run=True) == (100, 200)

def test_type_dry_run():
    assert type_text("hi", dry_run=True) == "hi"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_executor.py -v`
Expected: FAIL with "cannot import click_px"

- [ ] **Step 3: Write minimal implementation**

```python
import ctypes

def click_px(x: int, y: int, dry_run: bool = True) -> tuple[int, int]:
    if dry_run:
        return (x, y)
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
    return (x, y)

def type_text(text: str, dry_run: bool = True) -> str:
    if dry_run:
        return text
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.typewrite(text)
    return text
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_executor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add openastra/executor.py tests/test_executor.py
git commit -m "feat: add windows executor dry-run safe"
```

### Task 6: Agent loop + verifier + demo CLI

**Files:**
- Create: `openastra/agent.py`
- Create: `openastra/demo.py`
- Test: `tests/test_agent.py`

**Interfaces:**
- Consumes: `perceiver.screenshot`, `planner.StubPlanner.plan`, `grounder.CenterGrounder.ground`, `coords.denormalize`, `executor.click_px`
- Produces: `agent.run(task: str, max_steps: int = 20, dry_run: bool = True) -> dict`, `demo` CLI via `python -m openastra.demo --task "..." --dry-run`

- [ ] **Step 1: Write the failing test**

```python
from openastra.agent import run

def test_agent_dry_run_finishes():
    out = run("open notepad", max_steps=2, dry_run=True)
    assert out["steps"] == 2
    assert "log" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent.py -v`
Expected: FAIL with "cannot import run"

- [ ] **Step 3: Write minimal implementation**

```python
from openastra import perceiver, coords
from openastra.planner import StubPlanner
from openastra.grounder import CenterGrounder
from openastra.executor import click_px, type_text

def run(task: str, max_steps: int = 20, dry_run: bool = True) -> dict:
    planner = StubPlanner()
    grounder = CenterGrounder()
    history: list = []
    log: list = []
    for _ in range(max_steps):
        png, w, h = perceiver.screenshot() if not dry_run else (b"\x89PNG\r\n\x1a\n", 1920, 1080)
        intent = planner.plan(png, task, history)
        if intent.get("action") == "done":
            break
        x1000, y1000 = grounder.ground(png, w, h, intent.get("target", task))
        x, y = coords.denormalize(x1000, y1000, w, h)
        if intent.get("action") == "type":
            type_text(intent.get("text", ""), dry_run=dry_run)
        else:
            click_px(x, y, dry_run=dry_run)
        history.append(intent)
        log.append({"intent": intent, "x": x, "y": y})
        if len(history) >= max_steps:
            break
    return {"steps": len(history), "log": log}
```

`openastra/demo.py`:
```python
import argparse
from openastra.agent import run

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--max-steps", type=int, default=20)
    a = ap.parse_args()
    print(run(a.task, max_steps=a.max_steps, dry_run=a.dry_run))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/ -v`
Expected: PASS all

- [ ] **Step 5: Commit**

```bash
git add openastra/agent.py openastra/demo.py tests/test_agent.py
git commit -m "feat: add agent loop + demo CLI"
```
