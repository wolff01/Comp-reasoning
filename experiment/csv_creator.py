import sqlite3
import csv

def export_to_csv(db_name, csv_filename, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([desc[0] for desc in cursor.description])  # Column headers
        csv_writer.writerows(rows)
    
    conn.close()
    print(f"Database table '{table_name}' exported to {csv_filename}")

# Example usage
db_name = "clauderesults.db"  # Change this to your database file
csv_filename = "claude.csv"  # Change this to your desired CSV file name
table_name = "clauderesults"  # Change this to your table name
export_to_csv(db_name, csv_filename, table_name)
