import os
import json
from litellm import completion
from dotenv import load_dotenv
from prettytable import PrettyTable

load_dotenv()

answer = """You are playing the game of blackjack against a dealer at a casino. The table rules are as follows: dealer stands on a 17. If the dealer is showing a card with a 10 or greater value players may choose to insure their hands at half their bet. You have a 2 and a King; the dealer shows a 10. Respond what your choice is in this scenario using the following JSON schema:
{
"id":"",
"date":"",
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
results = []
try:
    response_content = response['choices'][0]['message']['content']
    results = response_content.split(', ')
    response_dict = json.loads(response_content)
except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
    # print(f"Error processing response: {e}")
    response_dict = None

file_path = 'gpt.json'
print(results)

try:
    with open(file_path, 'r') as file:
        results = json.load(file)
        if not isinstance(results, list):
            results = []

except FileNotFoundError:
    results = []

if response_dict:
    results.append(response_dict)

with open(file_path, 'w') as file:
    json.dump(results, file, indent=4)

# print("Result added successfully!")

def create_table(results):
    table = PrettyTable()
    table.field_names = ["ID", "Date", "Choice", "Reasoning"]

    table_data = []

    for item in results:
        if isinstance(item, dict):
            row = {
                "ID": item.get("id", "N/A"),
                "Date": item.get("date", "N/A"),
                "Choice": item.get("choice", "N/A"),
                "Reasoning": item.get("reasoning", "N/A")
            }
            table.add_row(list(row.values()))
            table_data.append(row)
        # else:
            # print(f"Skipping invalid item: {item}")

    print("\nTable of Results:")
    print(table)

    with open('gpttable.json', 'w') as table_file:
        json.dump(table_data, table_file, indent=4)
    # print("Table data saved to gpttable.json")

try:
    with open(file_path, 'r') as file:
        updated_results = json.load(file)
        if isinstance(updated_results, list):
            create_table(updated_results)
        else:
            print("Invalid data format in JSON file.")
except FileNotFoundError:
    print("No JSON file found.")
