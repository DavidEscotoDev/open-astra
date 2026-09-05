import ctypes

try:
    import pyautogui
    pyautogui.FAILSAFE = True
except ImportError:
    pass


def click_px(x: int, y: int, dry_run: bool = True) -> tuple[int, int]:
    if dry_run:
        return (x, y)
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
    return (x, y)


def type_text(text: str, dry_run: bool = True) -> str:
    if dry_run:
        return text
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.typewrite(text)
    return text


def press(key: str, dry_run: bool = True) -> str:
    if dry_run:
        return key
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.press(key)
    return key


def hotkey(*keys: str, dry_run: bool = True) -> tuple[str, ...]:
    if dry_run:
        return tuple(keys)
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.hotkey(*keys)
    return tuple(keys)
