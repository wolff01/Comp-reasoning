import sqlite3
import os
import csv

def run_query():
    # Define the paths to the database files
    database_files = ['clauderesults.db', 'geminiresults.db', 'blackjack_results.db']

    # Check if each database file exists
    for db_file in database_files:
        if not os.path.exists(db_file):
            print(f"Database file '{db_file}' not found.")
            return
    try:
        # Connect to an in-memory database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        # Attach external databases
        cursor.execute("ATTACH 'clauderesults.db' AS claude;")
        cursor.execute("ATTACH 'geminiresults.db' AS gemini;")
        cursor.execute("ATTACH 'blackjack_results.db' AS gpt;")

        # Define and execute the query, ensuring matching player_hand and dealer_card
        query = '''
        SELECT claude.clauderesults.player_hand, claude.clauderesults.dealer_card,
               claude.clauderesults.choice, gemini.geminiresults.choice, gpt.blackjack_results.choice
        FROM claude.clauderesults
        INNER JOIN gemini.geminiresults
        ON claude.clauderesults.player_hand = gemini.geminiresults.player_hand
        AND claude.clauderesults.dealer_card = gemini.geminiresults.dealer_card
        INNER JOIN gpt.blackjack_results
        ON claude.clauderesults.player_hand = gpt.blackjack_results.player_hand
        AND claude.clauderesults.dealer_card = gpt.blackjack_results.dealer_card;
        '''
        
        cursor.execute(query)
        results = cursor.fetchall()

        # Debugging: Print results before writing to CSV
        print("Fetched results:")
        for row in results:
            print(row)

        # Open a CSV file to write the results
        with open('choices.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write the header
            writer.writerow(['Player Hand', 'Dealer Card', 'Claude Choice', 'Gemini Choice', 'GPT Choice'])
            
            # Write the results
            for row in results:
                writer.writerow(row)

        print("Query results have been written to 'results.csv'.")

    except sqlite3.DatabaseError as e:
        print(f"Database error occurred: {e}")

    finally:
        # Ensure the connection is closed, even if an error occurred
        conn.close()

if __name__ == "__main__":
    run_query()
