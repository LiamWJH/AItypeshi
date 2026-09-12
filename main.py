from ollama import chat
import asyncio
import threading
import queue
import json
import time

from sight import sight
from tooling import *
from tooling import _get_memory_batch

result_queue = queue.Queue()
def run_sight():
  asyncio.run(sight())

threading.Thread(target=run_sight, daemon=True).start()


def say(message, stream=False, isPlain=False):
  if isPlain:
    print(f"<AI> {message}")
    return message
  if stream:
    print("<AI> ", end='')
    full_text = ""
    for chunk in message:
      text = chunk.message.content
      print(text, end='', flush=True)
      full_text += text
    print("")
    return full_text
  else:
    print(f"<AI> {message.message.content}")
    return message.message.content

def save_conversation_summary_for_session(reaction):
  global first_question, prev_userinput, prev_tool

  if first_question:
    first_question = not first_question
    return

  wascorrect = was_response_correct(prev_resp, reaction)

  messages = [{"role": "user", "content":  f"Write a factual one-sentence summary of this exchange, third person, no commentary, no questions, no meta-text. Try to make it as short as possible. User said: \"{prev_userinput}\" | AI replied: \"{prev_resp}\""}]
  response=chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
  )
  timestamp = time.time()
  local_struct = time.localtime(timestamp)
  formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_struct)


  with open("MEMORY.json", "r") as f:
    data = json.load(f)
  data.append({
    "correctanswer": wascorrect,
    "summary": response.message.content,
    "timestamp": formatted_time,
    "usedtool": prev_tool,
  })
  with open("MEMORY.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

def update_previous(resp, userinput, tool):
  global first_question, prev_resp, prev_userinput, prev_tool

  prev_resp = resp
  prev_userinput = userinput
  prev_tool = tool

def was_response_correct(resp, reaction):
  messages = [{"role": "assistant", "content": resp},
              {"role": "user", "content": f"First identify if the user's statement is related to your previous response, if not say 'UNRELATED' if it is a related response identify if the reaction claims your response was correct or not and answer in 'YES' or 'NO'. USER: {reaction}"
            }]
  response = chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
  )

  if response.message.content.capitalize() == 'NO':
    return False
  else:
    return True


running = True

prev_userinput = None
prev_resp = None
prev_tool = None
first_question = True

while running:
  userinput = input("> ")
  resp = None
  tool = None

  messages = [{"role": "user", "content": f"Determine if an action is needed for this task, and if so which task. for mouse/keyboard related actions, assume the cursor is already set to the right position. USERINPUT: '{userinput}'"}]
  response = chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
    tools=[get_memory_batch, get_sight_batch, click_mouse, pause_for]
  )


  if not response.message.tool_calls:
    save_conversation_summary_for_session(userinput)
    messages = [{"role": "user", "content": f"Answer the question/statement precisley and in a clean summarized way. If the user shows frustration ask for ways you could help them. QUESTION: '{userinput}'"}]
    response = chat(
      model='qwen3.5:9b',
      messages=messages,
      think=False,
      stream=True,
    )

    resp = say(response, stream=True)
    update_previous(resp, userinput, None)

    continue

  call = response.message.tool_calls[0]
  call_args = call.function.arguments
  call_result = None

  match call.function.name:
    case "pause_for":
      pause_for(**call_args)
      save_conversation_summary_for_session(userinput)
      resp = f"waited for {call.function.arguments["t"]} seconds"
      say(resp, isPlain=True)
      update_previous(resp, userinput, "pause_for")
      continue
    case "click_mouse":
      save_conversation_summary_for_session(userinput)
      threading.Thread(target=click_mouse, kwargs=call_args, daemon=True).start()
      resp = "clicked mouse"
      say(resp, isPlain=True)
      update_previous(resp, userinput, "click_mouse")
      continue
    case "get_sight_batch":
      save_conversation_summary_for_session(userinput)
      call_result = get_sight_batch(**call_args)
      messages.append(response.message)
      print(call_result)

      messages.append({
        "role": "user",
        "content": f"Answer the user's question directly and concisely, using the screenshost and summarized context only as supporting content if relevant. Don't describe the screenshots or contexts unless asked. Whenever the user refers to a screenshot or a picture they are referring to one in the screenshot provided, QUESTION: '{userinput}'",
        "images": call_result
      })
      final_response = chat(
        model='qwen3.5:9b',
        messages=messages,
        think=False,
        stream=True,
        options={"num_ctx": 16000}
      )

      resp = say(final_response, stream=True)
      update_previous(resp, userinput, "get_sight_batch")

      continue
    case "get_memory_batch":
      print(call_args, "hi nerd")
      save_conversation_summary_for_session(userinput)

      call_result = _get_memory_batch(**call_args, userinput=userinput)
      messages.append(response.message)
      messages.append({"role": "tool", "content": str(call_result)})
      messages.append({"role": "user", "content": f"Answer the user's question directly and concisely by using the given context if relevant. Don't describe the context unless asked. Question: {userinput}"})

      final_response = chat(
        model='qwen3.5:9b',
        messages=messages,
        think=False,
        stream=True,
        options={"num_ctx": 16000}
      )

      resp = say(final_response, stream=True)

      update_previous(resp, userinput, tool="get_memory_batch")
      continue
    case _:
      raise codefuckedup


  continue
