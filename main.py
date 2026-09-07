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



running = True
while running:
  userinput = input("> ")

  #we have to write function that does it without AI later so it gets faster
  '''messages = [{"role": "user", "content":
               f"""IDENTIFY THE TYPE OF CHAT THE USER WANTS FROM THE BELOW WITH THE CONDITION I GIVE:
                  0: Normal chat/
                  1: Sight/

                  CONDITIONS FOR EACH TYPE
                  0: Normal chat
                  - Any single words. example: "hi", "yo", "hey", "yes", "no"
                  - Any question that only requires elementary/middle/high school concept. examaple: "explain me entropy?", "what's a function?", "explain me fundamental physics"
                  1: Sight
                  - Any question or statement that directly or indirectly references things not included in question itself. example: "Whats on my screen?", "What's that round button gonna do?", "what is that image?", "look at that"
                  - Any question/statement that requires you to see what the objective is.
                  - Any question/statement that requires a screenshot of the screen.
                  - Any question/statement that you don't have the real time access to.
                  - Any question/statement that you can't answer without more user specification of the question.
                  IF NO CONDITION IS MET
                  1. Try finding the most fit amongst the given
                  2. If still none is found return Normal chat.

                  and return ONLY the CORRESPONDING NUMBER.

                  '{userinput}'
                  """}]
  response = chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
  )

  print(response.message.content)

  TEMPORARILY REMOVED DEVISION OF TASK
  '''
  '''
    match int(response.message.content):
      case 0:
        messages = [{"role": "user", "content": f"set the amount of screenshots needed for this task and return the path to them: '{userinput}'"}]
        response = chat(
          model='qwen3.5:9b',
          messages=messages,
          think=False,
          stream=False,
          tools=[get_sight_batch]
        )

        messages.append(response.message)

        if not response.message.tool_calls:
          print(f"<AI> {response.message.content}")
          continue

        call = response.message.tool_calls[0]
        result = get_sight_batch(**call.function.arguments)
        messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})
        print(result)
        final_messages = [{
          "role": "user",
          "content": f"Answer the user's question directly and concisely, using the screenshost only as supporting content if relevant. Don't describe the screenshots unless asked. Whenever the user refers to a screenshot or a picture they are referring to one in the screenshot provided,  Question: {userinput}",
          "images": result
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
      case 1:
        messages = [{"role": "user", "content": f"set the amount of screenshots needed for this task and return the path to them: '{userinput}'"}]
        response = chat(
          model='qwen3.5:9b',
          messages=messages,
          think=False,
          stream=False,
          tools=[get_sight_batch]
        )

        messages.append(response.message)

        if not response.message.tool_calls:
          print(f"<AI> {response.message.content}")
          continue

        call = response.message.tool_calls[0]
        result = get_sight_batch(**call.function.arguments)
        messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})
        print(result)
        final_messages = [{
          "role": "user",
          "content": f"Answer the user's question directly and concisely, using the screenshost only as supporting content if relevant. Don't describe the screenshots unless asked. Question: {userinput}",
          "images": result
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

  '''

  messages = [{"role": "user", "content": f"Determine what action is needed for this task, for mouse/keyboard related actions, assume the cursor is already set to the right position. : '{userinput}'"}]
  response = chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
    tools=[get_sight_batch, click_mouse, pause_for]
  )
  messages.append(response.message)


  if not response.message.tool_calls:
    print(f"<AI> {response.message.content}")
    continue

  call = response.message.tool_calls[0]

  if call.function.name == "pause_for":
      pause_for(**call.function.arguments)
      print(f"<AI> waited for {call.function.arguments["t"]} seconds")
      continue

  if call.function.name == "click_mouse":
    threading.Thread(target=click_mouse, kwargs=call.function.arguments, daemon=True).start()
    #result = click_mouse()
    print(f"<AI> clicked mouse")
    continue

  if call.function.name == "get_sight_batch":
    result = get_sight_batch(**call.function.arguments)
    messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})
    print(result)
    final_messages = [{
      "role": "user",
      "content": f"Answer the user's question directly and concisely, using the screenshost only as supporting content if relevant. Don't describe the screenshots unless asked. Whenever the user refers to a screenshot or a picture they are referring to one in the screenshot provided, Question: {userinput}",
      "images": result
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
    continue
