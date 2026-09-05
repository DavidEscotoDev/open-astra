from openastra.planner import StubPlanner


def test_stub_planner_click():
    p = StubPlanner()
    out = p.plan(b"fake-png", "open notepad", [])
    assert out["action"] in ("click", "type", "done")
    assert "target" in out
