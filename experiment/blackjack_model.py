CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

def calculate_hand_value(cards):
    value = sum(CARD_VALUES[card.title()] for card in cards)
    aces = cards.count('Ace')

    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return value

def play_blackjack(insert_player, insert_dealer):
    cards_player = ' '.join(insert_player)

    cards_dealer = ' '.join(insert_dealer)

    player = cards_player.split()
    dealer = cards_dealer.split()
    if 'and' in cards_player:
        cards_player.remove('and')
    if 'and' in cards_dealer:
        cards_dealer.remove('and')

    player_hand = player.copy()
    dealer_hand = dealer.copy()

    dealer_card_value = CARD_VALUES[dealer_hand[0].title()]

    while True:
        player_value = calculate_hand_value(player_hand)

        if player_value > 21:
            print("Bust! You exceeded 21. Dealer wins!")
            return
        
        if player_value < 9:
            if player_hand[0] == player_hand[1] and dealer_card_value <= 7:
                if len(player_hand) == 2:
                    return 'split'   
            else:
                return "hit"
        elif player_value == 9:
            if dealer_card_value == 2 or dealer_card_value >= 8:
                return "hit"
            else:
                return "double down"
        elif player_value == 10 or player_value == 11:
            if player_hand[0] == player_hand[1] and len(player_hand) == 2:
                return "double down"
            elif dealer_card_value < 11:
                return "double down"
            elif dealer_card_value == 11:
                return "hit"

        elif player_value == 12:
            if player_hand[0] == player_hand[1] and len(player_hand) == 2:
                if dealer_card_value < 7:
                    return "split"
                else:
                    return "hit"
            elif dealer_card_value <4:
                return "hit"
            elif 4 <= dealer_card_value < 7:
                return "stand"
            else:
                return "hit"

        elif player_value == 13 or player_value == 14:
            if player_hand[0] == player_hand[1] and len(player_hand) == 2:
                if dealer_card_value <= 7:
                    return "split"
                else:
                    return "hit"
            elif dealer_card_value < 7:
                return "stand"
            else:
                return "hit"

        elif player_value == 15 or player_value == 16:
            if player_hand[0] == player_hand[1] and len(player_hand) == 2:
                return "split"

            elif dealer_card_value < 7:
                return "stand"
            else:
                return "hit"

        elif player_value >= 17:
            if player_hand[0] == "Ace" and player_value == 17 and len(player_hand) == 2:
                if dealer_card_value >= 7:
                    return "hit"
                else:
                    return "double down"
            elif player_hand[0] == "Ace" and player_value == 18 and len(player_hand) == 2:
                if dealer_card_value < 7:
                    return "stand"
                else:
                    return "hit"
            elif player_hand[0] == "8" and player_hand[1] == "8" and len(player_hand) == 2:
                return "split"
            else:
                return "stand"

if __name__ == "__main__":
    play_blackjack()
