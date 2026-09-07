from ollama import chat
import pathlib
import os
import asyncio
import threading
import queue
import time

from sight import sight
from tooling import *

result_queue = queue.Queue()
def run_sight():
  asyncio.run(sight())

threading.Thread(target=run_sight, daemon=True).start()

def say(message, stream=False, isPlain=False):
  if isPlain:
    if stream:
      print("<AI> ", end='')
      for c in message:
        print(c, end='', flush=True)
      print("")
    else:
      print(f"<AI> {message}")
  else:
    if stream:
      print("<AI> ", end='')
      for chunk in message:
        print(chunk.message.content, end='', flush=True)
      print("")
    else:
        print(f"<AI> {message.message.content}")


running = True
while running:
  userinput = input("> ")

  messages = [{"role": "user", "content": f"Determine if an action is needed for this task, and if so which task. for mouse/keyboard related actions, assume the cursor is already set to the right position. : '{userinput}'"}]
  response = chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
    tools=[get_sight_batch, click_mouse, pause_for]
  )


  messages.append(response.message.content)

  if not response.message.tool_calls:
    messages = [{"role": "user", "content": f"Answer the question/statement precisley and in a clean summarized way. : '{userinput}'"}]
    response = chat(
      model='qwen3.5:9b',
      messages=messages,
      think=False,
      stream=True,
    )

    say(response, stream=True)
    continue

  call = response.message.tool_calls[0]
  call_args = call.function.arguments
  call_result = None

  match call.function.name:
    case "pause_for":
      pause_for(**call_args)
      say(f"waited for {call.function.arguments["t"]} seconds", isPlain=True)
      continue
    case "click_mouse":
      threading.Thread(target=click_mouse, kwargs=call_args, daemon=True).start()
      say(f"clicked mouse", isPlain=True)
      continue
    case "get_sight_batch":
      call_result = get_sight_batch(**call_args)
      messages.append({"role": "tool", "tool_name": call.function.name, "content": str(call_result)})
      print(call_result)

      final_messages = [{
        "role": "user",
        "content": f"Answer the user's question directly and concisely, using the screenshost only as supporting content if relevant. Don't describe the screenshots unless asked. Whenever the user refers to a screenshot or a picture they are referring to one in the screenshot provided, Question: {userinput}",
        "images": call_result
      }]
      final_response = chat(
        model='qwen3.5:9b',
        messages=final_messages,
        think=False,
        stream=True,
        options={"num_ctx": 16000}
      )

      say(final_response, stream=True)
      continue
    case _:
      raise codefuckedup
  continue
