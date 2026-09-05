from openastra.agent import run


def test_agent_dry_run_finishes():
    out = run("open notepad", max_steps=2, dry_run=True)
    assert out["steps"] == 2
    assert "log" in out


class ScriptedPlanner:
    def __init__(self, intents):
        self.intents = list(intents)

    def plan(self, shot, task, history):
        return self.intents.pop(0)


def test_agent_uses_injected_planner():
    planner = ScriptedPlanner([{"action": "done", "target": "", "text": ""}])
    out = run("anything", max_steps=5, dry_run=True, planner=planner)
    assert out["steps"] == 0

def test_agent_ollama_name_selects_model():
    from openastra.planner import OllamaPlanner
    import openastra.agent as agent_mod
    seen = {}
    real_init, real_plan = OllamaPlanner.__init__, OllamaPlanner.plan
    def fake_init(self, model="qwen2.5vl:3b"):
        seen["model"] = model
    def fake_plan(self, shot, task, history):
        return {"action": "done", "target": "", "text": ""}
    OllamaPlanner.__init__, OllamaPlanner.plan = fake_init, fake_plan
    try:
        out = agent_mod.run("t", max_steps=5, dry_run=True, planner="ollama", model="qwen2.5vl:3b")
    finally:
        OllamaPlanner.__init__, OllamaPlanner.plan = real_init, real_plan
    assert seen.get("model") == "qwen2.5vl:3b"
    assert out["steps"] == 0
