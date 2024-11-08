import json
import random

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
        choice.append(decision)
        print(f"Decision: {decision.capitalize()}")
        for hand in range(21):
            if decision == 'hit':
                hand = hit_hand(hand)
                if hand <= 21:
                    decision = random_decision()
                    print(f"Decision: {decision.capitalize()}")
                elif hand == 21:
                    print("21!!!!")
                    return hand
                elif hand >= 21:
                    print("Bust")
                    return hand
        return split, decision if not split else "split"

card_1 = int(input('Input card: '))
card_2 = int(input('Input card: '))
hand = [card_1, card_2]
choice = []
simulate_blackjack_hand(hand)

try:
    decision_dict = choice.to_dict()
except AttributeError:
    decision_dict = str(choice)

file_path = 'random.json'

try:
    with open(file_path, 'r') as file:
        results = json.load(file)
        if not isinstance(results, list):
            results = []
except FileNotFoundError:
    results = []

results.append(decision_dict)

with open(file_path, 'w') as file:
    json.dump(results, file, indent=4)

print("Result added successfully!")