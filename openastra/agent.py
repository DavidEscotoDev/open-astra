from openastra import perceiver, coords
from openastra.planner import StubPlanner, OllamaPlanner
from openastra.grounder import CenterGrounder, OllamaGrounder
from openastra.executor import click_px, type_text, press, hotkey


def run(task: str, max_steps: int = 20, dry_run: bool = True, planner=None, grounder=None, model: str = "qwen2.5vl:3b") -> dict:
    if planner is None:
        planner = StubPlanner()
    elif isinstance(planner, str):
        planner = OllamaPlanner(model=model) if planner == "ollama" else StubPlanner()
    if grounder is None:
        grounder = CenterGrounder()
    elif isinstance(grounder, str):
        grounder = OllamaGrounder(model=model) if grounder == "ollama" else CenterGrounder()
    history: list = []
    log: list = []
    for _ in range(max_steps):
        png, w, h = perceiver.screenshot()
        intent = planner.plan(png, task, history)
        if intent.get("action") == "done":
            break
        x1000, y1000 = grounder.ground(png, w, h, intent.get("target", task))
        x, y = coords.denormalize(x1000, y1000, w, h)
        if intent.get("action") == "type":
            type_text(intent.get("text", ""), dry_run=dry_run)
        elif intent.get("action") == "press":
            press(intent.get("text", "enter"), dry_run=dry_run)
        elif intent.get("action") == "hotkey":
            hotkey(*intent.get("text", "win").split("+"), dry_run=dry_run)
        else:
            click_px(x, y, dry_run=dry_run)
        history.append(intent)
        log.append({"intent": intent, "x": x, "y": y})
        if len(history) >= max_steps:
            break
    return {"steps": len(history), "log": log}
