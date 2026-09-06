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

def move_mouse_to(x,y):
    """Moves the user's cursor to a position with the x and y args that starts from the top left corner of the screen.

    Args:
      x: the x coordinate to move the cursor to
      y: the y coordinate to move the cursor to
    Returns:
      Nothing
    """
    pyautogui.moveTo(x, y, duration=0.6)