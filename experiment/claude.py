import os
import re
import json
from datetime import datetime
from litellm import completion
from dotenv import load_dotenv
import sqlite3

load_dotenv()

cards = input("Enter your cards: ").strip()

answer = f"""You are playing the game of blackjack against a dealer at a casino. The table rules are as follows: dealer stands on a 17. If the dealer is showing a card with a 10 or greater value, players may choose to insure their hands at half their bet. You have a {cards}; the dealer shows a 10. Respond with your choice using the following JSON schema:
{{
"choice":"",
"reasoning":""
}}"""

model = "claude"

try:
    response = completion(
        model=model,
        messages=[{
            "content": answer,
            "role": "user"
        }]
    )
except Exception as e:
    print(f"Error with model completion: {e}")
    response = None

now = datetime.now()
response_dict = None

if response:
    try:
        response_content = response['choices'][0]['message']['content']
        response_content = re.sub(r"```(\s+)?json(\s+)?\n(\s+)?|(\s+)?\n(\s+)?```", "", response_content)
        response_dict = json.loads(response_content)
        response_dict['id'] = response.get('id', f"manual_{now.timestamp()}")
        response_dict['model'] = response.get('model', model)
        response_dict['date'] = f"{now.year}-{now.month:02}-{now.day:02}"
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")

db_file = "results.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS blackjack_results (
    id TEXT PRIMARY KEY,
    model TEXT,
    date TEXT,
    choice TEXT,
    reasoning TEXT
)
""")

if response_dict:
    try:
        print("Inserting into SQLite:", response_dict)
        cursor.execute("""
        INSERT OR IGNORE INTO blackjack_results (id, model, date, choice, reasoning)
        VALUES (?, ?, ?, ?, ?)
        """, (
            response_dict.get("id"),
            response_dict.get("model"),
            response_dict.get("date"),
            response_dict.get("choice"),
            response_dict.get("reasoning")
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting into database: {e}")

def display_and_save_table():
    try:
        cursor.execute("SELECT * FROM blackjack_results")
        rows = cursor.fetchall()

        header = f"{'ID':<20} {'Model':<20} {'Date':<15} {'Choice':<15} {'Reasoning':<50}"
        table = [header, "-" * len(header)]

        for row in rows:
            table.append(f"{row[0]:<20} {row[1]:<20} {row[2]:<15} {row[3]:<15} {row[4]:<50}")

        print("\n".join(table))

        with open("claudetable.txt", "w") as file:
            file.write("\n".join(table))
        print("\nTable has been saved to table.txt")
    except sqlite3.Error as e:
        print(f"Error displaying or saving data: {e}")

display_and_save_table()

conn.close()
