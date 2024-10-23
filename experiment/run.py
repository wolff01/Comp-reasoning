import os 
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

print(os.environ["OPENAI_API_KEY"])

# openai call
response = completion(
    model = "gpt-4o", 
    messages=[{ "content": "Hello, how are you?","role": "user"}]
)
print(response)

