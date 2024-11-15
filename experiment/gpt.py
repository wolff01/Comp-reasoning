import os
import json
from litellm import completion
from dotenv import load_dotenv
import sqlite3

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

try:
    response_content = response['choices'][0]['message']['content']
    response_dict = json.loads(response_content)
    print("Response Dictionary:", response_dict)
except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
    print(f"Error processing response: {e}")
    response_dict = None

db_file = "results.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS blackjack_results (
    id TEXT PRIMARY KEY,
    date TEXT,
    choice TEXT,
    reasoning TEXT
)
""")

if response_dict:
    print("Inserting into SQLite:", response_dict)
    cursor.execute("""
    INSERT OR IGNORE INTO blackjack_results (id, date, choice, reasoning)
    VALUES (?, ?, ?, ?)
    """, (response_dict.get("id"), response_dict.get("date"), response_dict.get("choice"), response_dict.get("reasoning")))
    conn.commit()

cursor.execute("SELECT * FROM blackjack_results")
rows = cursor.fetchall()
print("Current Database Rows:", rows)

def display_table():
    cursor.execute("SELECT * FROM blackjack_results")
    rows = cursor.fetchall()

    header = f"{'ID':<20} {'Date':<20} {'Choice':<15} {'Reasoning':<50}"
    print(header)
    print("-" * len(header))

    for row in rows:
        print(f"{row[0]:<20} {row[1]:<20} {row[2]:<15} {row[3]:<50}")

try:
    display_table()
except Exception as e:
    print(f"Error displaying data: {e}")

conn.close()
