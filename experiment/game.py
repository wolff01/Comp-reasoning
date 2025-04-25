from random import shuffle
from time import time
import sqlite3
import experiment

CARDS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
SHOE_SIZE = 6

def initialize_shoe():
    cards = CARDS * 4 * SHOE_SIZE
    shuffle(cards)
    return cards

def deal_card(shoe):
    return shoe.pop() if shoe else None

def card_value(card):
    return 10 if card in ["Jack", "Queen", "King"] else 11 if card == "Ace" else str(card)


def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = hand.count("Ace")
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def play_player(shoe, dealer_hand):
    hand = [deal_card(shoe), deal_card(shoe)]
    response_data = experiment.get_blackjack_decision(hand, dealer_hand)
    db_name = "gptresults.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    choice = experiment.save_to_database(cursor, response_data)
    while True:
        experiment.main(hand, dealer_hand)
        if choice == "hit":
            hand.append(deal_card(shoe))
            if hand_value(hand) > 21:
                break
        else:
            break
    return hand

def play_dealer(shoe):
    hand = [deal_card(shoe)]
    while hand_value(hand) < 17 and shoe:
        hand.append(deal_card(shoe))
    return hand

def play_round(shoe):
    dealer_hand = play_dealer(shoe)
    player_hand = play_player(shoe, dealer_hand)
    
    player_score, dealer_score = hand_value(player_hand), hand_value(dealer_hand)

    if player_score > 21:
        print("Result: Dealer wins!\n")
        return -1
    elif dealer_score > 21 or player_score > dealer_score:
        print("Result: Player wins!\n")
        return 1
    elif dealer_score > player_score:
        print("Result: Dealer wins!\n")
        return -1
    else:
        print("Result: It's a tie...\n")
        return 0

if __name__ == "__main__":
    start_time = time()
    shoe = initialize_shoe()
    wins, loses, number_of_games = 0, 0, 0

    while shoe:
        result = play_round(shoe)
        wins += result == 1
        loses += result == -1
        number_of_games += 1
    
    print(f"Number of games: {number_of_games}\n")
    print(f"Player Success: {round((wins / number_of_games) * 100, 2)}%\n")
    print(f"\nTime to execute: {time() - start_time:.2e} seconds")
