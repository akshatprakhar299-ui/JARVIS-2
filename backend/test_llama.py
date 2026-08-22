import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Create Groq client
client = Groq(api_key=api_key)

# Send message to Llama
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are JARVIS, a helpful personal AI assistant."
        },
        {
            "role": "user",
            "content": "Hello JARVIS. Introduce yourself in two sentences."
        }
    ],
    temperature=0.7
)

# Print response
print("\nJARVIS:")
print(response.choices[0].message.content)