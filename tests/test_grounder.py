from openastra.grounder import CenterGrounder


def test_center_grounder():
    g = CenterGrounder()
    assert g.ground(b"png", 1920, 1080, "Search box") == (500, 500)


def test_agent_ollama_grounder_name_selects_model():
    from openastra.grounder import OllamaGrounder
    import openastra.agent as agent_mod
    seen = {}
    real_init, real_ground = OllamaGrounder.__init__, OllamaGrounder.ground
    def fake_init(self, model="qwen2.5vl:3b"):
        seen["model"] = model
    def fake_ground(self, shot, w, h, target):
        return (100, 200)
    OllamaGrounder.__init__, OllamaGrounder.ground = fake_init, fake_ground
    try:
        out = agent_mod.run("t", max_steps=1, dry_run=True, grounder="ollama", model="qwen2.5vl:3b")
    finally:
        OllamaGrounder.__init__, OllamaGrounder.ground = real_init, real_ground
    assert seen.get("model") == "qwen2.5vl:3b"
    from openastra import perceiver
    _, w, h = perceiver.screenshot()
    assert out["log"][0]["x"] == int(100 / 1000 * w)
    assert out["log"][0]["y"] == int(200 / 1000 * h)
