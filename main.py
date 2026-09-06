from ollama import chat
import pathlib
import os
import asyncio

from sight import sight

# parts of the code is from the ollama documentation: you can probably tell from the existence of comments ig
def get_temperature(city: str) -> str:
  """Get the current temperature for a city

  Args:
    city: The name of the city

  Returns:
    The current temperature for the city
  """
  temperatures = {
    "New York": "22°C",
    "London": "15°C",
    "Tokyo": "18°C",
  }
  return temperatures.get(city, "Unknown")

def get_last_sight_batch():
  sight_dir = pathlib.Path().resolve() / "vision_mem"
  sights = sorted(os.listdir(sight_dir), key=lambda x: os.path.getmtime(os.path.join(sight_dir, x)))
  return sights[-12:]

running = True
while running:
  userinput = input("> ")

  #we have to write function that does it without AI later so it gets faster
  messages = [{"role": "user", "content":
               f"""IDENTIFY THE TYPE OF CHAT THE USER WANTS FROM THE BELOW WITH THE CONDITION I GIVE:
                  0: Normal chat/
                  1: Sight/
                  2: Advanced chat/

                  CONDITIONS FOR EACH TYPE
                  0: Normal chat
                  - Any single words. example: "hi", "yo", "hey", "yes", "no"
                  - Any question that only requires elementary/middle/high school concept. examaple: "explain me entropy?", "what's a function?", "explain me fundamental physics"
                  1: Sight
                  - Any question or statement that directly or indirectly references things not included in question itself. example: "Whats on my screen?", "What's that round button gonna do?", "what is that image?", "look at that"
                  - Any question/statement that requires you to see what the objective is.
                  - Any question/statement that requires a screenshot of the screen.
                  2: Advanced chat
                  - Areas that require specialized knowledge to explain. example: "Explain linked lists", "Explain fermat's last theorm"
                  - Questions that request you to solve a problem. Example: "Write a function to find the longest common prefix string amongst an array of strings. If there is no common prefix, return an empty string "".", "x plus xy plus y is 3, x to the power of two multiplied with y plus x multiplied with y to the power of 2 is -70, what is x and what is y?"

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
  match int(response.message.content):
    case 0:
      messages = [{"role": "user", "content": userinput}]

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
    case 1:
      print("c1")
      images = get_last_sight_batch()
      messages = [{"role": "user", "content": userinput, "images": images}]

      response = chat(
        model='qwen3.5:9b',
        messages=messages,
        think=False,
        stream=True,
      )
      print("<AI> ", end='')
      for chunk in response:
        print(chunk.message.content, end='', flush=True)
      pass
    case 2:
      messages = [{"role": "user", "content": userinput}]

      response = chat(
        model='qwen3.8:27b',
        messages=messages,
        think=False,
        stream=True,
      )
      print("<AI> ", end='')
      for chunk in response:
        print(chunk.message.content, end='', flush=True)
      print("")

  asyncio.run(sight())

"""response = chat(model="qwen3.5:2b", messages=messages, tools=[get_temperature], think=False)"""

"""messages.append(response.message)
if response.message.tool_calls:
  # only recommended for models which only return a single tool call
  call = response.message.tool_calls[0]
  result = get_temperature(**call.function.arguments)
  # add the tool result to the messages
  messages.append({"role": "tool", "tool_name": call.function.name, "content": str(result)})

  final_response = chat(model="qwen3.5:2b", messages=messages, tools=[get_temperature], think=False)
  print(final_response.message.content)"""