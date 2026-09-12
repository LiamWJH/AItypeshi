import pathlib
import time
import pyautogui
import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("intfloat/e5-large-v2")

class codefuckedup(Exception):
  pass

''' COMMENTED OUT BC IT INTERFERS WITH GET MEMORY BATCH
def get_recent_memory_batch(n: int):
  """Gives access to our most recent several conversation that occured outside current chat session that was between the user and you. so you can use it for more context to answer the user's question.

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
'''

def get_memory_batch(n:int):
  """Gives access to our previous conversation that occured outside current chat session by getting the relevant conversation that is relevant to the userinput that was between the user and you. so you can use it for more context to answer the user's question.

  Args:
    n: the maximum amount of past conversation this tool will return

  Returns:
    The relevant past conversations.
  """

def _get_memory_batch(userinput: str, n: int):
  results = []
  with open("memory.json", "r") as f:
    data = json.loads(f.read())
    for summary in data:
      question = f"query: {userinput}"
      answer = f"passage: {summary['summary']}"
      embeddings = model.encode([question, answer], normalize_embeddings=True)
      similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
      results.append((similarity, summary))
  results.sort(key=lambda x: x[0], reverse=True)
  print(results)
  top = results[:n]
  memorybuf = ""
  for score, mem in top:
    tag = f' [used tool: {mem["usedtool"]}]' if mem.get("usedtool") else ""
    memorybuf += f'[{mem["timestamp"]}] [AI correct: [{"YES" if mem["correctanswer"] else "NO"}]]{tag} {mem["summary"]}\n'
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