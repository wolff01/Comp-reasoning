import os
import re
import json
import sqlite3
from datetime import datetime
from litellm import completion
from dotenv import load_dotenv
import blackjack_model
import game

load_dotenv()

MODEL_MAP = {
    "gemini": "gemini/gemini-1.5-pro",
    "gpt": "o1-mini",
    "claude": "anthropic/claude-3-5-sonnet"
}

def get_blackjack_decision(cards, dealer):
    """Generate blackjack decision using AI models."""
    prompt = f"""You are playing the game of blackjack against a dealer at a casino. The table rules are as follows: 
    - Dealer stands on 17.
    - If the dealer is showing a 10 or Ace, you may take insurance.
    - If insurance is not taken, you must choose: hit, stand, split, double down, or surrender on the first two cards.
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
            model=MODEL_MAP["gpt"],
            messages=[{"content": prompt, "role": "user"}]
        )
        response_content = response['choices'][0]['message']['content']
        response_content = re.sub(r"```json\n|\n```", "", response_content).strip()
        return json.loads(response_content)
    except Exception as e:
        print(f"Error with model completion: {e}")
        return None

def get_blackjack_model_result(cards, dealer):
    """Compare AI decision with `blackjack_model.play_blackjack()`"""
    try:
        result = blackjack_model.play_blackjack(cards, dealer)
        if isinstance(result, (list, dict, str)):
            return json.dumps(result)
        return "Unexpected return type"
    except Exception as e:
        print(f"Error in blackjack model: {e}")
        return "Error"

def setup_database(db_name):
    """Create and connect to SQLite database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blackjack_results (
        model TEXT,
        date TEXT,
        choice TEXT,
        reasoning TEXT,
        compare TEXT
    )""")
    conn.commit()
    return conn, cursor

def save_to_database(cursor, response_data):
    """Insert response data into the database."""
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO blackjack_results (model, date, choice, reasoning, compare)
        VALUES (?, ?, ?, ?, ?)""", (
            response_data.get("model"),
            response_data.get("date"),
            response_data.get("choice"),
            response_data.get("reasoning"),
            response_data.get("compare")
        ))
        piece = [response_data.get("choice")]
        return str(piece)
    except sqlite3.Error as e:
        print(f"Database insertion error: {e}")

def save_table_to_file(cursor, file_path):
    """Save database table to a text file."""
    try:
        cursor.execute("SELECT * FROM blackjack_results")
        rows = cursor.fetchall()
        header = f"{'Model':<20} {'Date':<15} {'Choice':<15} {'Reasoning':<50} {'Compare':<10}"
        table = [header, "-" * len(header)]
        table.extend([f"{row[0]:<20} {row[1]:<15} {row[2]:<15} {row[3]:<50} {row[4]:<10}" for row in rows])
        with open(file_path, "w") as file:
            file.write("\n".join(table))
        print(f"Table saved to {file_path}")
    except sqlite3.Error as e:
        print(f"Error saving table: {e}")

def main(cards, dealer):
    now = datetime.now()

    response_data = get_blackjack_decision(cards, dealer)
    if not response_data:
        print("Failed to get AI decision.")
        return
    response_data['model'] = "o1-mini"
    response_data['date'] = now.strftime("%Y-%m-%d")
    response_data['compare'] = get_blackjack_model_result(cards, dealer)
    
    databases = {
        "gpt": setup_database("gptresults.db"),
    }

    for model, (conn, cursor) in databases.items():
        save_to_database(cursor, response_data)
        conn.commit()
        save_table_to_file(cursor, f"{model}table.txt")
        conn.close()

if __name__ == "__main__":
    main()
