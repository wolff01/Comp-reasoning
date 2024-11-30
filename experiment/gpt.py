import os
import re
import json
from datetime import datetime
from litellm import completion
from dotenv import load_dotenv
import sqlite3

load_dotenv()

answer = """You are playing the game of blackjack against a dealer at a casino. The table rules are as follows: dealer stands on a 17. If the dealer is showing a card with a 10 or greater value players may choose to insure their hands at half their bet. You have a 2 and a King; the dealer shows a 10. Respond what your choice is in this scenario using the following JSON schema:
{
"choice":"",
"reasoning":""
}"""

model = "gpt-4o"

response = completion(
    model=model,
    messages=[{
        "content": answer,
        "role": "user"
    }]
)

now = datetime.now()

try:
    response_content = response['choices'][0]['message']['content']
    response_content = re.sub("```(\s+)?json(\s+)?\\n(\s+)?|(\s+)?\\n(\s+)?```","",response_content)
    response_dict = json.loads(response_content)
    response_dict['id'] = response['id']
    response_dict['model'] = response['model']
    response_dict['date'] = f"{now.year}-{now.month}-{now.day}"
except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
    response_dict = None

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
    print("Inserting into SQLite:", response_dict)
    cursor.execute("""
    INSERT OR IGNORE INTO blackjack_results (id, model, date, choice, reasoning)
    VALUES (?, ?, ?, ?, ?)
    """, (response_dict.get("id"), response_dict.get("model"), response_dict.get("date"), response_dict.get("choice"), response_dict.get("reasoning")))
    conn.commit()

cursor.execute("SELECT * FROM blackjack_results")
rows = cursor.fetchall()

def display_table():
    cursor.execute("SELECT * FROM blackjack_results")
    rows = cursor.fetchall()

    header = f"{'ID':<20} {'model':<20} {'Date':<20} {'Choice':<15} {'Reasoning':<50}"
    print(header)
    print("-" * len(header))

    for row in rows:
        print(f"|{row[0]:<20} | {row[1]:<20} | {row[2]:<15} | {row[3]:<50}| {row[4]:<20}")

try:
    display_table()
except Exception as e:
    print(f"Error displaying data: {e}")

conn.close()
