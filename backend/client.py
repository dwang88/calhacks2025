# for structure
from letta_client import Letta
import os
from dotenv import load_dotenv

load_dotenv()

client = Letta(token=os.getenv("LETTA_API_KEY"))

agent = client.agents.create(
    model="anthropic/claude-3-5-sonnet-20241022",
    embedding="openai/text-embedding-3-small",
    # optional configuration
    context_window_limit=30000,
    tools=['web_search']
)

response = client.agents.messages.create(
  agent_id=agent.id,
  messages=[
    {
      "role": "user",
      "content": "What is the weather in Tokyo?"
    }
  ]
)

for message in response.messages:
  print(message)