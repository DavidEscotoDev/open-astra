def clamp1000(v: int) -> int:
    return max(0, min(1000, int(v)))


def denormalize(x1000: int, y1000: int, w: int, h: int) -> tuple[int, int]:
    return (int(clamp1000(x1000) / 1000 * w), int(clamp1000(y1000) / 1000 * h))
