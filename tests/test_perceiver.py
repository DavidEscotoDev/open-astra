from openastra.perceiver import screenshot

def test_screenshot_returns_png_and_size():
    png, w, h = screenshot()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert w > 0 and h > 0
