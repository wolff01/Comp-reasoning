#Blackjack AI Decision System
This Python application simulates a simplified game of Blackjack and leverages multiple LLMs (Gemini, GPT, and Claude) to recommend a move—Hit, Stand, Split, Double Down, or Surrender—based on your initial hand and the dealer's card.

##Features
Prompts Large Language Models (LLMs) to make decisions using realistic blackjack rules.

Stores each model's decision, reasoning, and input cards into a local SQLite database.

Supports models via LiteLLM for unified inference.

###Required packages:

litellm

python-dotenv

sqlite3 (built-in with Python)

re, json, datetime (built-in)

##Notes
Currently, the system assumes two-card player hands and one dealer card.

LLM behavior may vary slightly depending on their internal knowledge and version.

You can expand the database schema or logic to simulate full hands and track game outcomes.
