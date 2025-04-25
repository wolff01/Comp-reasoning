import os
import re
import json
import sqlite3
import time
from datetime import datetime
from dotenv import load_dotenv
from litellm import completion
from concurrent.futures import ThreadPoolExecutor, as_completed

CARDS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

load_dotenv()

MODEL_MAP = {
    "gemini": "gemini/gemini-1.5-pro",
    "gpt": "o1-mini",
    "claude": "anthropic/claude-3-5-sonnet-20241022"
}

def get_blackjack_decision(model_key, player_hand, dealer_card, retries=3, delay=3):
    prompt = f"""You are playing blackjack against a dealer. The rules:
    - Dealer stands on 17.
    - You can hit, stand, split, double down, or surrender.
    - With 3+ cards, you can only hit or stand.

    Your hand: {player_hand}  
    Dealer's card: {dealer_card}  

    Respond in JSON format:
    {{
        "choice": "",
        "reasoning": ""
    }}"""

    for attempt in range(1, retries + 1):
        try:
            response = completion(
                model=MODEL_MAP[model_key],
                messages=[{"role": "user", "content": prompt}]
            )
            content = response["choices"][0]["message"]["content"]
            content = re.sub(r"```json\n|\n```", "", content).strip()
            result = json.loads(content)
            result.update({
                "model": model_key,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "player_hand": player_hand,
                "dealer_card": dealer_card
            })
            return result
        except Exception as e:
            print(f"[{model_key}] Attempt {attempt} failed: {e}")
            if "503" in str(e) or "overloaded" in str(e).lower():
                if attempt < retries:
                    print(f"[{model_key}] Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"[{model_key}] All retries failed. Skipping.")
            else:
                break
    return None

def setup_database(db_name="results.db"):
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
        )
    """)
    conn.commit()
    return conn, cursor

def save_to_database(cursor, conn, data):
    try:
        cursor.execute("""
            INSERT INTO clauderesults (model, date, choice, reasoning, player_hand, dealer_card)
            VALUES (?, ?, ?, ?, ?, ?)""", (
            data["model"],
            data["date"],
            data["choice"],
            data["reasoning"],
            json.dumps(data["player_hand"]),
            data["dealer_card"]
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def play_blackjack():
    conn, cursor = setup_database()

    card1 = input("Card 1: ").strip().upper()
    card2 = input("Card 2: ").strip().upper()
    dealer_card = input("Dealer Card: ").strip().upper()
    player_hand = [card1, card2]

    print(f"Player Hand: {player_hand}")
    print(f"Dealer Card: {dealer_card}")

    cursor.execute("""
        INSERT INTO clauderesults (model, date, choice, reasoning, player_hand, dealer_card)
        VALUES (?, ?, ?, ?, ?, ?)""", (
        "initial",
        datetime.now().strftime("%Y-%m-%d"),
        "",
        "Initial deal",
        json.dumps(player_hand),
        dealer_card
    ))
    conn.commit()

    with ThreadPoolExecutor(max_workers=len(MODEL_MAP)) as executor:
        futures = {
            executor.submit(get_blackjack_decision, key, player_hand, dealer_card): key
            for key in MODEL_MAP
        }

        for future in as_completed(futures):
            model_key = futures[future]
            result = future.result()
            if result:
                print(f"\n{model_key.upper()} Decision:\nChoice: {result['choice']}\nReasoning: {result['reasoning']}")
                save_to_database(cursor, conn, result)
            else:
                print(f"{model_key.upper()} failed to return a decision.")

    conn.close()
    print("\nAll models completed. Game over.")

if __name__ == "__main__":
    play_blackjack()
