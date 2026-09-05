class CenterGrounder:
    def ground(self, shot: bytes, w: int, h: int, target: str) -> tuple[int, int]:
        return (500, 500)


class OllamaGrounder:
    def __init__(self, model: str = "qwen2.5vl:3b"):
        self.model = model

    def ground(self, shot: bytes, w: int, h: int, target: str) -> tuple[int, int]:
        import json
        import base64
        import io
        import re
        import urllib.request
        from PIL import Image
        img = Image.open(io.BytesIO(shot))
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        payload = json.dumps({
            "model": self.model, "stream": False,
            "prompt": f'Look at this screenshot. Find "{target}". Reply with ONLY this JSON, no other text: {{"x": 0-1000, "y": 0-1000}} where 0,0 is top-left and 1000,1000 bottom-right.',
            "images": [b64]}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode())
        content = data["response"].strip()
        mx = re.search(r'"?x"?\s*:\s*(\d+)', content)
        my = re.search(r'"?y"?\s*:\s*(\d+)', content)
        if not mx or not my:
            raise ValueError(f"no coordinates in model output: {content[:200]}")
        return (max(0, min(1000, int(mx.group(1)))), max(0, min(1000, int(my.group(1)))))
# ponytail: VLM guess, swap with OS-Atlas-7B local when accuracy matters
