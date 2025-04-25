import csv
import ast  # To safely evaluate string representations of Python literals

CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def calculate_hand_value(cards):
    """Calculate the total hand value, adjusting for Aces."""
    value = sum(CARD_VALUES[card.title()] for card in cards)
    aces = cards.count('A')

    while value > 21 and aces > 0:
        value -= 10  # Convert Ace from 11 to 1
        aces -= 1

    return value

def play_blackjack(insert_player, insert_dealer):
    """Determine the best move based on player's and dealer's hands."""
    first_dealer_card = insert_dealer[0].title()
    if first_dealer_card not in CARD_VALUES:
        return "Invalid dealer card"

    dealer_card_value = CARD_VALUES[first_dealer_card]
    player_value = calculate_hand_value(insert_player)
    is_pair = len(insert_player) == 2 and insert_player[0] == insert_player[1]

    if player_value > 21:
        return "Bust! You exceeded 21. Dealer wins!"
    
    if player_value < 9:
        return "split" if is_pair and dealer_card_value <= 7 else "hit"

    elif player_value == 9:
        return "double down" if dealer_card_value not in [2, 8, 9, 10, 11] else "hit"

    elif player_value in [10, 11]:
        return "double down" if dealer_card_value < 10 else "hit"

    elif player_value == 12:
        return "split" if is_pair and dealer_card_value < 7 else ("stand" if 4 <= dealer_card_value < 7 else "hit")

    elif player_value in [13, 14]:
        return "split" if is_pair and dealer_card_value <= 7 else ("stand" if dealer_card_value < 7 else "hit")

    elif player_value in [15, 16]:
        return "split" if is_pair else ("stand" if dealer_card_value < 7 else "hit")

    elif player_value >= 17:
        if is_pair and insert_player[0] == "8":
            return "split"
        return "stand"

def clean_player_hand(raw_hand):
    """Fix formatting issues in player hand and convert to a list."""
    try:
        fixed_hand = raw_hand.replace('""', '"')  # Fix extra double quotes
        return ast.literal_eval(fixed_hand)
    except (ValueError, SyntaxError):
        return None  # Return None if parsing fails

def check_mismatch(ai_decision, user_decision, player_hand):
    """Check for mismatches and return appropriate values."""
    is_pair = len(player_hand) == 2 and player_hand[0] == player_hand[1]

    if ai_decision == "split" and not is_pair:
        return "2"  # Mark 2 if split is recommended but hand isn't a pair
    return "1" if ai_decision.lower() != user_decision else "0"  # Regular mismatch check

def read_csv_and_play_blackjack(input_filename, output_filename):
    """Reads a CSV file, plays blackjack based on the player's hand, compares decisions, and writes results."""
    updated_rows = []

    with open(input_filename, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Read the header row
        
        # Add "AI Decision" and "Mismatch" columns if not already present
        if "AI Decision" not in headers:
            headers.append("AI Decision")
        if "Claude Mismatch" not in headers:
            headers.append("Claude Mismatch")
        if "Gemini Mismatch" not in headers:
            headers.append("Gemini Mismatch")
        if "ChatGPT Mismatch" not in headers:
            headers.append("ChatGPT Mismatch")

        updated_rows.append(headers)

        for row in csv_reader:
            if len(row) > 3:  # Ensure row has enough columns
                raw_hand = row[0].strip()
                player_hand = clean_player_hand(raw_hand)  # Fix and convert hand

                dealer_hand = row[1].strip().replace('"', '')  # Ensure dealer card is clean
                user_decision_3 = row[2].strip().lower()  # Read row 3 (existing decision)
                user_decision_4 = row[3].strip().lower()  # Read row 4 (existing decision)
                user_decision_5 = row[4].strip().lower()  # Read row 5 (existing decision)

                if player_hand is None:
                    ai_decision = "Error: Invalid player hand format"
                    claude_mismatch = ""
                    gemini_mismatch = ""
                    gpt_mismatch = ""
                else:
                    ai_decision = play_blackjack(player_hand, [dealer_hand])
                    claude_mismatch = check_mismatch(ai_decision, user_decision_3, player_hand)
                    gemini_mismatch = check_mismatch(ai_decision, user_decision_4, player_hand)
                    gpt_mismatch = check_mismatch(ai_decision, user_decision_5, player_hand)

                row.append(ai_decision)
                row.append(claude_mismatch)
                row.append(gemini_mismatch)
                row.append(gpt_mismatch)

            updated_rows.append(row)

    # Write the updated rows to a new CSV file
    with open(output_filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(updated_rows)

if __name__ == "__main__":
    input_csv = 'choices.csv'  # Replace with your input CSV filename
    output_csv = 'output.csv'  # New file where results will be saved
    read_csv_and_play_blackjack(input_csv, output_csv)
    print(f"Results saved to {output_csv}")
