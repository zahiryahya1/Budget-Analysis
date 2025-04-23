import csv
import sys
import os
from collections import defaultdict
from bank_cleaner_helper import printChoices

def clean_amount(amount):
    return float(amount.replace('$', '').replace(',', ''))

def clean_date(date):
    month, day, year = date.split('/')
    
    # hacky way of fixing university bank year given as 2 digit instread of 20xx
    year = int(year)
    if year < 100:  # 2-digit year
        year += 2000
    return f"{year}-{month}-{day}"

def categorize_transaction(payee, categories):
    payee_lower = payee.lower()
    if "spectrum" in payee_lower:
        if "center dr" in payee_lower:
            return None
        if "ppd id" in payee_lower or "spectrum spectrum" in payee_lower:
            return "Fixed, Utilities"
        
    for category, keywords in categories.items():
        if any(keyword.lower() in payee_lower for keyword in keywords):
            print("found a match")
            print(category)
            print(payee_lower)
            print(keywords)
            return category
    return None

def prompt_for_category(date, amount, description, payee, remaining_uncategorized):
    print(f"Transactions left to categorize: {remaining_uncategorized}")
    print(f"\nTransaction Details:")
    print(f"Date: {date}")
    print(f"Amount: ${amount:.2f}")
    print(f"Payee: {payee}")
    printChoices()

    choice_map = {
        "1": "Grocery/Cleaning", "G": "Grocery/Cleaning",
        "2": "Transportation", "C": "Transportation",
        "3": "Dining Out", "D": "Dining Out",
        "4": "Together Activity", "T": "Together Activity",
        "5": "Friends + Family", "F": "Friends + Family",
        "6": "Household Good", "H": "Household Good",
        "7": "Rent", "R": "Rent",
        "8": "Utilities", "U": "Utilities",
        "9": "Medical", "M": "Medical",
        "10": "K Discretionary", "K": "K Discretionary",
        "11": "Z Discretionary", "Z": "Z Discretionary",
        "12": "Other", "O": "Other",
        "S": "skip"
    }

    while True:
        choice = input("Enter a number or letter (or S to skip): ").strip().upper()
        if choice in choice_map:
            return choice_map[choice]
        print("Invalid choice. Please try again.")

def detect_bank_format(headers):
    if "Posting Date" in headers and "Description" in headers:
        return "Chase"
    elif "Date" in headers and "Description" in headers and 'Running Bal.' in headers:
        return "BOA"
    elif "Posted Date" in headers and "Payee" in headers:
        return "BOA"
    elif "Account ID" in headers and "Transaction ID" in headers:
        return "UCU"
    elif "Transaction Date" in headers and "Description" in headers and "Amount (USD)" in headers:
        return "Apple"
    elif "Date" in headers and "Description" in headers and "" in headers:
        return "Wells Fargo"
    else:
        return "Unknown"

def bank_cleaner(input_files):
    categories = {
        "Fixed, Utilities": {"spectrum", "water", "electricity", "so cal gas", "LADWP"},
        "Fixed, Subscription": {"netflix", "spotify", "amazon prime", "Amazon web services"},
        "Variable, Grocery/Cleaning": {"ralphs", "vons", "trader joes", "trader joe", "whole foods", "WHOLEFDS", "PAVILIONS", "costco", "smart and final", "target"},
        "Variable, Transportation": {"shell", "chevron", "mobile", "car wash", "honda", "DMV", "UBER", "SOUTHWES"},
        "Variable, Household Good": {"walmart", "ikea", "homedepot", "living spaces", "home goods", "ace", "HOMEGOODS"},
        "Fixed, Rent": {"lido", "LEMONADE INSURANCE"},
        "Variable, Dining Out": {"fat tomato", "pizza", "don antonios", "mcdonalds", "starbucks", "nekter", "THAI FRESH", "DOMINO'S"},
        "Fixed, Medical": {"rite aid", "walgreens", "cvs", "LMFT", "Paulas Choice", "CHEMISTRY RX"},
        "Income, Salary": {"CULVER CITY UNIF SCHOOL", "UNIVERSITY OF CA", "REMOTE ONLINE DEPOSIT"}
    }

    cleaned_data = [["Date", "Payment Amount ($)", "Payee", "Category", "Subcategory", "Category Type", "Account", "Description"]]
    uncategorized_transactions = []

    for input_file in input_files:
        with open(input_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            bank_type = detect_bank_format(headers)
            transactions = list(reader)

            for row in transactions:
                date = clean_date(row.get('Transaction Date', row.get('Posting Date', row.get('Date', row.get('Posted Date', '')))))
                payee = row.get('Description', row.get('Payee', ''))
                amount = clean_amount(row.get('Amount (USD)', row.get('Amount', '0')))
                
                # apple transaction are opposite. need to switch
                if bank_type == "Apple":
                    amount = -amount
                    
                description = row.get('Description', '')

                category = categorize_transaction(payee, categories)
                if category:
                    _, sub_category = category.split(', ')
                    cleaned_data.append([date, f"{amount:.2f}", payee, "", sub_category, "", bank_type, ""])
                else:
                    uncategorized_transactions.append((date, amount, description, payee, bank_type))

    for i in range(len(uncategorized_transactions)):
        date, amount, description, payee, bank_type = uncategorized_transactions[i]
        user_choice = prompt_for_category(date, amount, description, payee, len(uncategorized_transactions) - i)
        if user_choice == "skip":
            continue
        sub_category = user_choice
        cleaned_data.append([date, f"{amount:.2f}", payee, "", sub_category, "", bank_type, ""])

    output_file = "clean_transactions.csv"
    with open(output_file, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(cleaned_data)

    print(f"Cleaned file saved to {output_file}")

if __name__ == "__main__":
    input_csvs = sys.argv[1:]
    bank_cleaner(input_csvs)
