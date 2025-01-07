import json
import random
from datetime import datetime

# Deck of cards
deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 11]

def random_decision():
    return random.choice(['hit', 'stand'])

def random_split_decision():
    return random.choice([True, False])

def hit_hand(hand):
    new_card = int(input("Input Card: "))
    hand += new_card
    return hand

def simulate_blackjack_hand(hand):
    print(f"Initial hand: {hand}")
    if hand[0] == hand[1]:
        split = random_split_decision()
        if split:
            print("Decision: Split the hand!")
        else:
            print("Decision: Do not split.")
    else:
        split = False

    if not split:
        decision = random_decision()
        choice.append(f"{decision} | {hand}")
        print(f"Decision: {decision.capitalize()}")
        while sum(hand) < 21:  # Use sum(hand) to compare the total hand value
            if decision == 'hit':
                new_card = int(input("Input Card: "))  # Input new card
                hand.append(new_card)  # Add new card to the hand
                print(f"New hand: {hand} (Total: {sum(hand)})")
                if sum(hand) < 21:
                    decision = random_decision()
                    choice.append(f"{decision} | {hand}")
                    print(f"Decision: {decision.capitalize()}")
                elif sum(hand) == 21:
                    print("21!!!!")
                    choice.append(f"21 | {hand}")
                    break
                else:
                    print("Bust")
                    choice.append(f"Bust | {hand}")
                    break
            elif decision == 'stand':
                choice.append(f"Stand | {hand}")
                break
        return split, decision if not split else "split"

# Input initial cards
card_1 = int(input('Input card: '))
card_2 = int(input('Input card: '))
hand = [card_1, card_2]
choice = []

simulate_blackjack_hand(hand)

# Save results to rando.txt
file_path = 'rando.txt'
try:
    with open(file_path, 'r') as file:
        results = file.read().splitlines()
except FileNotFoundError:
    results = []

# Get current date and time
current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Add results with date, model, hand, and decisions
model_name = "Random Decision Model"
results.append(f"{current_date} | {model_name} | Initial hand: {hand}")
for entry in choice:
    results.append(f"{current_date} | {model_name} | {entry}")

with open(file_path, 'w') as file:
    file.write("Date | Model | Choice/Hand\n")  # Header for the table
    file.write("\n".join(results))

print("Result added successfully to rando.txt!")
