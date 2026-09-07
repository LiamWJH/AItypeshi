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

class reponse:
  def __init__(self, call_tool, response):
    self.call_tool = call_tool
    self.response = response
  def say(self, ):
    print("<AI> ", end='')
    for chunk in response:
      print(chunk.message.content, end='', flush=True)
    print("")

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

    print("<AI> ", end='')
    for chunk in response:
      print(chunk.message.content, end='', flush=True)
    print("")
    continue

  call = response.message.tool_calls[0]
  call_result = None

  # match tool -> use tool -> notify tool was used -> break
  # what we want to add: know user input + AI response -> after each response store to DB or json file or smth for tool to pull
  # if we end up using json we use classes bc they look cool and nice
  # i should probably do OOP so it is cleaner.
  # userinput variable + the print that was used = one chat
  # fuck DB i dont want to learn sql im going for json.
  # so i guess store the userinput and response as a class? or maybe just add to the json file after each response?
  # but then i have to print the result too so it becomes repetitve and dirty to see
  # maybe i should make a response class and make a inherited class of tool_response
  # lets try and roll back if it's shi
  match call.function.name:
    case "pause_for":
      pause_for(**call.function.arguments)
      print(f"<AI> waited for {call.function.arguments["t"]} seconds")
      break
    case "click_mouse":
      threading.Thread(target=click_mouse, kwargs=call.function.arguments, daemon=True).start()
      print(f"<AI> clicked mouse")
      break
    case "get_sight_batch":
      call_result = get_sight_batch(**call.function.arguments)
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

      print("<AI> ", end='')
      for chunk in final_response:
        print(chunk.message.content, end='', flush=True)
      print("")
      break
  continue
