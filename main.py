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

def save_conversation_summary_for_session(user, response, wasCorrectResp, whichtool):
  global first_question
  if first_question:
    return 0;
  messages = [{"role": "user", "content":  f"Write a factual one-sentence summary of this exchange, third person, no commentary, no questions, no meta-text. Try to make it as short as possible. User said: \"{user}\" | AI replied: \"{response}\""}]
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
    "correctanswer": wasCorrectResp,
    "summary": response.message.content,
    "timestamp": formatted_time,
    "usedtool": whichtool,
  })
  with open("MEMORY.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

def was_response_correct(resp, reaction):
  messages = [{"role": "assistant", "content": resp},
              {"role": "user", "content": f"Answer in either 'YES' or 'NO' ONLY. Did the user like the response you gave (if these is no specific reaction to the response say 'YES')? USER: {reaction}"
            }]
  response = chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
  )

  if response.message.content.capitalize() == 'YES':
    return True
  else:
    return False


running = True

prev_userinput = None
prev_resp = None
first_question = True

while running:
  userinput = input("> ")
  resp = None

  messages = [{"role": "user", "content": f"Determine if an action is needed for this task, and if so which task. for mouse/keyboard related actions, assume the cursor is already set to the right position. USERINPUT: '{userinput}'"}]
  response = chat(
    model='qwen3.5:9b',
    messages=messages,
    think=False,
    stream=False,
    tools=[get_memory_batch, get_sight_batch, click_mouse, pause_for]
  )

  messages.append(response.message.content)

  if not response.message.tool_calls:
    messages = [{"role": "user", "content": f"Answer the question/statement precisley and in a clean summarized way. If the user shows frustration ask for ways you could help them. QUESTION: '{userinput}'"}]
    response = chat(
      model='qwen3.5:9b',
      messages=messages,
      think=False,
      stream=True,
    )

    resp = say(response, stream=True)

    save_conversation_summary_for_session(prev_userinput, prev_resp, was_response_correct(prev_resp, userinput), None)
    continue

  call = response.message.tool_calls[0]
  call_args = call.function.arguments
  call_result = None

  match call.function.name:
    case "pause_for":
      pause_for(**call_args)
      say(f"waited for {call.function.arguments["t"]} seconds", isPlain=True)
      save_conversation_summary_for_session(prev_userinput, f"waited for {call.function.arguments["t"]} seconds", was_response_correct(prev_resp, userinput), "pause_for")
      continue
    case "click_mouse":
      threading.Thread(target=click_mouse, kwargs=call_args, daemon=True).start()
      say(f"clicked mouse", isPlain=True)
      save_conversation_summary_for_session(userinput, f"clicked mouse", was_response_correct(prev_resp, userinput), "click_mouse")
      continue
    case "get_sight_batch":
      call_result = get_sight_batch(**call_args)
      messages.append({"role": "tool", "tool_name": call.function.name, "content": str(call_result)})
      print(call_result)

      final_messages = [{
        "role": "user",
        "content": f"Answer the user's question directly and concisely, using the screenshost and summarized context only as supporting content if relevant. Don't describe the screenshots or contexts unless asked. Whenever the user refers to a screenshot or a picture they are referring to one in the screenshot provided, QUESTION: '{userinput}'",
        "images": call_result
      }]
      final_response = chat(
        model='qwen3.5:9b',
        messages=final_messages,
        think=False,
        stream=True,
        options={"num_ctx": 16000}
      )

      resp = say(final_response, stream=True)
      save_conversation_summary_for_session(userinput, resp, was_response_correct(prev_resp, userinput), "get_sight_batch")
      continue
    case "get_memory_batch":
      print(call_args, "hi nerd")
      call_result = _get_memory_batch(**call_args, userinput=userinput)
      messages.append({"role": "assistant", "content": response.message.content})
      messages.append({"role": "tool", "tool_name": call.function.name, "content": str(call_result)})
      messages.append({"role": "user", "content": f"Answer the user's question directly and concisely by using the given context if relevant. Don't describe the context unless asked. Question: {userinput}"})

      final_response = chat(
        model='qwen3.5:9b',
        messages=messages,
        think=False,
        stream=True,
        options={"num_ctx": 16000}
      )

      resp = say(final_response, stream=True)
      save_conversation_summary_for_session(userinput, resp, was_response_correct(prev_resp, userinput), "get_memory_batch")
      continue
    case _:
      raise codefuckedup

  prev_userinput = userinput
  prev_resp = resp
  continue
