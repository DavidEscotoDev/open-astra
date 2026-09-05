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
