import csv
import ast

def convert_to_numbers(card_list):
    card_values = {"K": 10, "Q": 10, "J": 10, "A": 11}
    return [card_values.get(card, int(card)) for card in card_list]

def count_21_with_stand(file_path):
    count = 0

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 6:
                try:
                    card_list = ast.literal_eval(row[5])  
                    numbers = convert_to_numbers(card_list)
                    
                    if sum(numbers) > 21 and row[3].strip().lower() == "split":
                        count += 1
                except (ValueError, SyntaxError):
                    pass

    print(f"Count of sums equal to 21 with 'stand' in the third column: {count}")

count_21_with_stand('claude.csv')

