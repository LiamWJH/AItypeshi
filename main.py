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
  messages = [{"role": "user", "content": input("> ")}]

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