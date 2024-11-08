import os
import json
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

answer = """You are playing the game of blackjack against a dealer at a casino. The table rules are as follows: dealer stands on a 17. If the dealer is showing a card with a 10 or greater value players may choose to insure their hands at half their bet. You have a 2 and a King; the dealer shows a 10. Respond what your choice is in this scenario using the following JSON schema:
{
"choice":"",
"reasoning":""
}"""

response = completion(
    model="gpt-4o", 
    messages=[{
        "content": answer,
        "role": "user"
    }]
)

try:
    response_dict = response.to_dict()
except AttributeError:
    response_dict = str(response)



file_path = 'gpt.json'

try:
    with open(file_path, 'r') as file:
        results = json.load(file)
        if not isinstance(results, list):
            results = []
except FileNotFoundError:
    results = []

results.append(response_dict)

with open(file_path, 'w') as file:
    # TODO: iterate on results[-1].choices[-1].message.content
    json.dump(results, file, indent=4)

print("Result added successfully!")
