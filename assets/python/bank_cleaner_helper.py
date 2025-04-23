import sys
import csv

    
def csv_reader(csv_file_path):
    
    transactionsList = []
    
    with open(csv_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:            
            transactionsList.append(row)
                 
    return transactionsList


def printChoices():
    print("\n1. Grocery/Cleaning")
    print("2. Car/Transportation")
    print("3. Dining Out")
    print("4. Together Activity")
    print("5. Friends + Fam")
    print("6. Household Goods")    
    print("7. Rent")
    print("8. Utilities")
    print("9. Medical")
    print("10. K Discretionary")
    print("11. Z Discretionary")
    print("12. Other")
    print("13. Skip")

    
