from openastra.agent import run


def test_agent_dry_run_finishes():
    out = run("open notepad", max_steps=2, dry_run=True)
    assert out["steps"] == 2
    assert "log" in out
