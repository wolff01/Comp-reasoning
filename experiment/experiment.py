import os
import re
import json
import sqlite3
from datetime import datetime
from litellm import completion
from dotenv import load_dotenv

CARDS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

load_dotenv()

MODEL_MAP = {
    "gemini": "gemini/gemini-1.5-pro",
    "gpt": "o1-mini",
    "claude": "anthropic/claude-3-5-sonnet-20241022"
}

def get_blackjack_decision(model_key, cards, dealer):
    """Generate blackjack decision using AI models."""
    prompt = f"""You are playing blackjack against a dealer. The rules:
    - Dealer stands on 17.
    - You can hit, stand, split, double down, or surrender.
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
            model=MODEL_MAP[model_key],
            messages=[{"content": prompt, "role": "user"}]
        )
        response_content = response['choices'][0]['message']['content']
        response_content = re.sub(r"```json\n|\n```", "", response_content).strip()
        return json.loads(response_content)
    except Exception as e:
        print(f"Error with {model_key} model completion: {e}")
        return None

def setup_database(db_name):
    """Create and connect to SQLite database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clauderesults (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT,
        date TEXT,
        choice TEXT,
        reasoning TEXT,
        player_hand TEXT,
        dealer_card TEXT
    )""")
    conn.commit()
    return conn, cursor

def save_to_database(cursor, conn, response_data):
    """Insert response data into the database."""
    try:
        cursor.execute("""
        INSERT INTO clauderesults (model, date, choice, reasoning, player_hand, dealer_card)
        VALUES (?, ?, ?, ?, ?, ?)""", (
            response_data.get("model"),
            response_data.get("date"),
            response_data.get("choice"),
            response_data.get("reasoning"),
            json.dumps(response_data.get("player_hand")),
            response_data.get("dealer_card")
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database insertion error: {e}")

def play_blackjack():
    conn, cursor = setup_database("results.db")
    
    insert_card_1 = input("Card 1: ")
    insert_card_2 = input("Card 2: ")
    player_hand = [insert_card_1, insert_card_2]
    dealer_card = input("Dealer Card: ")
    print(f"Player's Initial Hand: {player_hand}")
    print(f"Dealer's Initial Card: {dealer_card}")
    
    # Insert initial hands into the database
    cursor.execute("""
    INSERT INTO clauderesults (model, date, choice, reasoning, player_hand, dealer_card)
    VALUES (?, ?, ?, ?, ?, ?)""", ("initial", datetime.now().strftime("%Y-%m-%d"), "", "Initial deal", json.dumps(player_hand), dealer_card))
    conn.commit()
    
    for model_key in MODEL_MAP.keys():
        decision = get_blackjack_decision(model_key, player_hand, dealer_card)
        if not decision:
            print(f"AI decision failed for {model_key}.")
            continue
        
        print(f"{model_key.upper()} Decision: {decision}")
        decision["model"] = model_key
        decision["date"] = datetime.now().strftime("%Y-%m-%d")
        decision["player_hand"] = player_hand
        decision["dealer_card"] = dealer_card
        
        save_to_database(cursor, conn, decision)
    
    conn.close()
    print("Game over!")

if __name__ == "__main__":
    play_blackjack()
