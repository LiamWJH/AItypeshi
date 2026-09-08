import pathlib
import time
import pyautogui
import json

class codefuckedup(Exception):
  pass

STOPWORDS = {"a","an","the","is","was","were","you","i","me","my","when","time","did","do","does","to","of","in","on","for","and","or","but","use","using","it","that","this","how","what"}

def get_recent_memory_batch(n: int):
  """Gives access to our previous conversation history by getting the most recent several conversation between the user and you from a database so you can use for reference.

  Args:
    n: The number of past summarized conversations that will be picked as reference.

  Returns:
    The summarized past conversations between the user and the AI.
  """
  relevant = []
  with open("memory.json", "r") as f:
    data = json.loads(f.read())
    data.reverse()
    relevant = []
    i = 0
    while i < n:
      relevant.append(data[i])
      i += 1

    if len(relevant) == 0: raise codefuckedup

    memorybuf = ""
    for mem in relevant:
      if mem["usedtool"] == None:
        memorybuf += f'[{mem["timestamp"]}] {mem["summary"]}\n'
      else:
        memorybuf += f'[{mem["timestamp"]}] [used tool: {mem["usedtool"]}] {mem["summary"]}\n'

    return memorybuf

def get_memory_batch(search_kw: list[str], n: int):
  """Gives access to our previous conversation history by searching for conversations between the user and you from a database that have the relevant keywords of the question past so you can use for reference.

  Args:
    search_kw: A list of keywords that should be choosed from the content user's question/statement that the user explicitly states or is implicitly referenced which is going to be searched up in the whole memory database for relevant memory.
    n: The number of past summarized conversations that will be picked as reference.

  Returns:
    The summarized past conversations between the user and the AI.
  """
  return _get_memory_batch(search_kw, n, og_prompt=None)

def _get_memory_batch(search_kw: list[str], n: int, og_prompt=None):
  """Internal tool cause if registered as ollama it gonna go weird and autistic"""
  if n > 20: n = 20

  relevant = []
  with open("memory.json", "r") as f:
    data = json.loads(f.read())
    data.reverse()
    for section in data:
      if len(relevant) >= n: break
      sum = section["summary"]
      for kw in search_kw:
        if kw.lower() in STOPWORDS: continue
        if kw in sum and section not in relevant:
            relevant.append(section)

    if len(relevant) == 0 and og_prompt:
      for section in data:
        if len(relevant) >= n: break
        sum = section["summary"]
        for kw in og_prompt:
          if kw.lower() in STOPWORDS: continue
          if kw in sum and section not in relevant:
              relevant.append(section)

    if len(relevant) == 0:
      relevant = data[:n]

    memorybuf = ""
    for mem in relevant:
      if mem["usedtool"] == None:
        memorybuf += f'[{mem["timestamp"]}] {mem["summary"]}\n'
      else:
        memorybuf += f'[{mem["timestamp"]}] [used tool: {mem["usedtool"]}] {mem["summary"]}\n'

    return memorybuf

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