import pathlib
import time
import pyautogui

class codefuckedup(Exception):
  pass

def get_sight_batch(n: int):
    """Gets the recent screenshot/screenshots of the user's screen

    Args:
      n: the number of images to grab from
    Returns:
      The recent screenshot/screenshots of the user's screen
    """
    if n > 5:
      n = 5
    sight_dir = pathlib.Path(__file__).resolve().parent / "vision_mem"
    sights = sorted(sight_dir.iterdir(), key=lambda p: p.stat().st_mtime)
    #r_batch = [str(p) for p in sights[-n:]]
    all_batch = sights[-n:]
    i = 0
    while i < len(all_batch):
      p = all_batch[i]
      if time.time() - p.stat().st_mtime > 60:
        all_batch.pop(i)
        continue
      else:
        i += 1
    if len(all_batch) == 0:
      raise codefuckedup
    return all_batch

def click_mouse(clicks: int, interval: float, button: str):
    """Clicks the left or middle or right button on the mouse on certain interval and certain amount of clicks

    Args:
      clicks: the amount of clicks to do
      interval: the time between clicks in seconds
      button: either the 'left' or 'right' or 'middle' to specify which button to press
    Returns:
      Nothing
    """
    time.sleep(0.2)
    pyautogui.click(clicks=clicks, interval=interval, button=button)

def pause_for(t: int):
    """Does nothing and pauses for certain amount of seconds

    Args:
      t: the amount of seconds that for nothing to be done
    Returns:
      Nothing
    """
    time.sleep(t)