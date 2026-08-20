from ollama import chat

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

running = True
while running:
  userinput = input("> ")
  messages = [{"role": "user", "content":
               f"""IDENTIFY THE TYPE OF CHAT THE USER WANTS FROM THE BELOW WITH THE CONDITION I GIVE:
                  0: Normal chat/
                  1: Sight/
                  2: Advanced chat/

                  CONDITIONS FOR EACH TYPE
                  0: Normal chat
                  - Any formal words. example: "hi", "yo", "hey"
                  - Any question that only requires elementary/middle/high school concept. examaple: "explain me entropy?", "what's a function?", "explain me fundamental physics"
                  1: Sight
                  - Any question or statement that directly or indirectly references things not included in question itself. example: "Whats on my screen?", "What's that round button gonna do?", "what is that image?", "look at that"
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