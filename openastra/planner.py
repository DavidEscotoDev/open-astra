import json
import urllib.request


class StubPlanner:
    def plan(self, shot: bytes, task: str, history: list) -> dict:
        return {"action": "click", "target": task, "text": ""}


class OllamaPlanner:
    def __init__(self, model: str = "qwen2.5vl:3b"):
        self.model = model

    def plan(self, shot: bytes, task: str, history: list) -> dict:
        import base64
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(shot))
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        payload = json.dumps({
            "model": self.model, "stream": False,
            "prompt": f"Look at this screenshot. Task: {task}. History: {history}. Reply with ONLY this JSON, no other text: {{\"action\": \"click|type|done\", \"target\": \"...\", \"text\": \"...\"}}",
            "images": [b64]}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode())
        content = data["response"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        obj, _ = json.JSONDecoder().raw_decode(content[content.index("{"):])
        return {"action": obj.get("action", "click"), "target": obj.get("target", task), "text": obj.get("text", "")}
