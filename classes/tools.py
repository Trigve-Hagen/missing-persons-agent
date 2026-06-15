import json
from langchain_core.tools import tool

# ---------------------------------------------------------
# tools
# ---------------------------------------------------------

@tool
def get_current_weather(location):
  """Get the current weather for a specific city location.

  Args:
      location: The name of the city, e.g., 'San Francisco'
  """
  weather_info = {
    "location": location,
    "temperature": "72",
    "unit": "fahrenheit",
    "forcast": ["sunny", "windy"],
  }
  return json.dumps(weather_info)
