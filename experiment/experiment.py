import os
import re
import json
from datetime import datetime
from litellm import completion
from dotenv import load_dotenv
import blackjack_model
import sqlite3

load_dotenv()

model = ""

model_input = input("Input model name: ").strip().lower()
if model_input == "gemini":
    model = "gemini/gemini-1.5-pro"
elif model_input == "gpt":
    model = "o1-mini"
elif model_input == "claude":
    model = "anthropic/claude-3-5-sonnet-20240620"
else:
    raise ValueError("Invalid model name. Choose from 'gemini', 'gpt', or 'claude'.")

cards = input("Enter your cards: ").strip()
dealer = input("Enter dealer card: ").strip()

answer = f"""You are playing the game of blackjack against a dealer at a casino. The table rules are as follows: 
- Dealer stands on 17.
- If the dealer is showing a 10 or Ace, you may take insurance.
- If insurance is not taken, you must choose: hit, stand, split, or double down on the first two cards.
- With 3+ cards, you can only hit or stand.

Your hand: {cards}  
Dealer's card: {dealer}  

Respond in JSON format:
{{
    "choice": "",
    "reasoning": ""
}}"""

try:
    response = completion(
        model=model,
        messages=[{"content": answer, "role": "user"}]
    )
except Exception as e:
    print(f"Error with model completion: {e}")
    response = None

now = datetime.now()
response_dict = None

if response:
    try:
        response_content = response['choices'][0]['message']['content']
        response_content = re.sub(r"```json\n|\n```", "", response_content)  # Clean JSON formatting
        response_dict = json.loads(response_content)
        response_dict['id'] = response.get('id', f"manual_{now.timestamp()}")
        response_dict['model'] = response.get('model', model)
        response_dict['date'] = now.strftime("%Y-%m-%d")
        response_dict['compare'] = str(blackjack_model)  # Convert to string
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")

db_file = f"{model_input}_results.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Fix SQL syntax error (missing comma)
cursor.execute("""
CREATE TABLE IF NOT EXISTS blackjack_results (
    id TEXT PRIMARY KEY,
    model TEXT,
    date TEXT,
    choice TEXT,
    reasoning TEXT,
    compare TEXT
)
""")

if response_dict:
    try:
        print(response_dict)
        cursor.execute("""
        INSERT OR IGNORE INTO blackjack_results (id, model, date, choice, reasoning, compare)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            response_dict["id"],
            response_dict["model"],
            response_dict["date"],
            response_dict["choice"],
            response_dict["reasoning"],
            response_dict["compare"]
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting into database: {e}")

def display_and_save_table():
    try:
        cursor.execute("SELECT * FROM blackjack_results")
        rows = cursor.fetchall()

        header = f"{'ID':<20} {'Model':<20} {'Date':<15} {'Choice':<15} {'Reasoning':<50} {'Compare':<10}"
        table = [header, "-" * len(header)]

        for row in rows:
            table.append(f"{row[0]:<20} {row[1]:<20} {row[2]:<15} {row[3]:<15} {row[4]:<50} {row[5]:<10}")

        with open(f"{model_input}table.txt", "w") as file:
            file.write("\n".join(table))
        print(f"\nTable has been saved to {model_input}_table.txt")
    except sqlite3.Error as e:
        print(f"Error displaying or saving data: {e}")

display_and_save_table()

conn.close()
