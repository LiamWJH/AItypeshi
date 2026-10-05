import pathlib
import time
import pyautogui
import json
import subprocess
import os
import sys
from sentence_transformers import SentenceTransformer, util
from ollama import chat
from overlay import Overlay, TextHud

ROW_H = 80
COL_W = 220
START_X = 100
START_Y = 100
MAX_Y = 950
ROWS = (MAX_Y - START_Y) // ROW_H
active = {}

def next_slot():
  for slot in list(active):
    if active[slot].poll() is not None:
      del active[slot]
  slot = 0
  while slot in active:
    slot += 1
  return slot

def slot_to_xy(slot):
  col, row = divmod(slot, ROWS)
  return START_X + col * COL_W, START_Y + row * ROW_H

stransformer_model = SentenceTransformer("intfloat/e5-large-v2")
model = "gemma4:12b"

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

def do_task():
  """Extends your capability by giving you the capability to write a python script that will run on the user's PC, which can perform more complicated tasks such as making software that functions as tools or etc.

  Args:

  Returns:
    The user's wanted output.
  """

def _do_task(prompt):
  messages = [{"role": "system", "content": "You control the user's computer through python scripts. Reply with a python script that fullfills the user's need. No summary of what you did, no markdown formatted text or parts of code, only the code."},
              {"role": "user", "content": prompt}
              ]
  response = chat(
    model=model,
    messages=messages,
    think=True,
    stream=False,
    options={"num_ctx": 16000}
  )
  messages = [{"role": "system", "content": "You choose the name of python scripts from the code. Reply with a short descriptive name, do not write the .py file extension."},
              {"role": "user", "content": response.message.content}
              ]
  name_response = chat(
    model=model,
    messages=messages,
    think=False,
    stream=False,
    options={"num_ctx": 16000}
  )
  with open(os.path.join("AItaskscripts", name_response.message.content+".py"), "w", encoding="utf-8") as f:
    f.write(response.message.content)

    f.close()

  def run_command(command: list[str]):
      proccess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")

      ret = ""
      for output in proccess.stdout:
          ret += output
          print(output, end='')
      return ret

  result = ""
  while response.message.content != 'success':
    try:
      result, retcode = run_command(["python", os.path.join("AItaskscripts", name_response.message.content+".py")])
    except Exception as e:
      print(e)
      raise codefuckedup
    if retcode == 1:
      messages = [{"role": "system", "content": "Identify if this result from running a python code needs an enviornmental fix (eg. package installing), or a fix of code. If an enviornmental fix is needed reply with ENV followed by the prompt you will run in the terminal, if it's a code change reply only with the whole code rewritten with any markdown formatting."},
                  {"role": "user", "content": result}
                  ]
      response = chat(
        model=model,
        messages=messages,
        think=True,
        stream=False,
        options={"num_ctx": 16000}
      )
      print(response.message.content)
      if 'ENV' in response.message.content.lower()[0:5]:
        r2 = subprocess.run(response.message.content, shell=True, text=True, capture_output=True)
        print(r2.stdout)
        print(r2.stderr)
      else:
        with open(os.path.join("AItaskscripts", name_response.message.content+".py"), "w", encoding="utf-8") as f:
          f.write(response.message.content)

          f.close()
    else:
      return

# idk man imma just add buncha shit options
def start_timer(t: int):
  """Starts a timer that counts down.

  Args:
    t: the amount of second the count down starts from

  Returns:
    Nothing
  """
  slot = next_slot()
  x, y = slot_to_xy(slot)
  active[slot] = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "AItools", "timer.py"), str(t), str(x), str(y)])

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
      embeddings = stransformer_model.encode([question, answer], normalize_embeddings=True)
      similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
      results.append((similarity, summary))
  results.sort(key=lambda x: x[0], reverse=True)
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

def write_on_kb(sentence: str):
  """Writes desired sentence on any input with the keyboard.

  Args:
    sentence: the input to write
  Returns:
    Nothing
  """
  time.sleep(0.2)
  pyautogui.write(sentence, interval=0.04)

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