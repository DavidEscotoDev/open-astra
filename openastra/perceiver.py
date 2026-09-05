import mss
from mss.tools import to_png

def screenshot() -> tuple[bytes, int, int]:
    with mss.MSS() as sct:
        mon = sct.monitors[1]
        shot = sct.grab(mon)
        return (to_png(shot.rgb, shot.size), shot.width, shot.height)
