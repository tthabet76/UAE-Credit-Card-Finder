"""
[Run Once] Adds the salary column to the database.
"""
import sqlite3
import re

DB_PATH = r'C:\Users\cdf846\Documents\personal\Credit card project\credit_card_data.db'

def parse_salary(salary_str):
    """
    Parses a salary string to find the lowest numeric value.
    Example: "AED 5,000 (for employees) or AED 12,500" -> 5000.0
    """
    if not salary_str or salary_str in ["Not Mentioned", "Not Found", "-"]:
        return 0.0
    
    # Remove commas
    clean_str = str(salary_str).replace(',', '')
    
    # Find all numbers (integers or floats)
    # We look for sequences of digits, possibly followed by a dot and more digits
    matches = re.findall(r'\d+\.?\d*', clean_str)
    
    if not matches:
        return 0.0
        
    # Convert to floats
    values = []
    for m in matches:
        try:
            val = float(m)
            # Filter out likely non-salary numbers (e.g. "1" card, "2024" year) if needed
            # For now, we assume any large number is a salary. 
            # But let's just take all valid floats.
            values.append(val)
        except ValueError:
            continue
            
    if not values:
        return 0.0
        
    # Return the minimum value found (e.g. "5000 or 10000" -> 5000)
    return min(values)

def migrate_salary_column():
    print("--- Adding and Populating 'min_salary_numeric' ---")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Add Column (ignore if exists)
        try:
            cursor.execute("ALTER TABLE credit_cards_details ADD COLUMN min_salary_numeric REAL DEFAULT 0.0")
            print("Column 'min_salary_numeric' added.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("Column 'min_salary_numeric' already exists.")
            else:
                raise e
        
        # 2. Fetch all rows
        cursor.execute("SELECT url, minimum_salary_requirement FROM credit_cards_details")
        rows = cursor.fetchall()
        print(f"Processing {len(rows)} records...")
        
        updated_count = 0
        for row in rows:
            url = row['url']
            raw_salary = row['minimum_salary_requirement']
            numeric_salary = parse_salary(raw_salary)
            
            # Update the row
            cursor.execute("UPDATE credit_cards_details SET min_salary_numeric = ? WHERE url = ?", (numeric_salary, url))
            updated_count += 1
            
        conn.commit()
        print(f"Successfully updated {updated_count} records.")
        
        # Verification
        print("\nSample Verification:")
        cursor.execute("SELECT minimum_salary_requirement, min_salary_numeric FROM credit_cards_details LIMIT 10")
        for row in cursor.fetchall():
            print(f"  '{row[0]}' -> {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_salary_column()
