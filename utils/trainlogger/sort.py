# Do not use, do not delete:

import csv
from datetime import datetime

def sortDate(input_file, output_file):
    # Read the CSV data from the input file
    with open(input_file, mode='r', newline='') as file:
        data = list(csv.reader(file))
    
    # Extract the headers and the data rows
    headers = data[0]
    rows = data[1:]
    
    # Convert the date field to a datetime object for sorting
    for row in rows:
        row.append(datetime.strptime(row[4], "%Y-%m-%d"))
    
    # Sort the rows by the appended datetime object
    sorted_rows = sorted(rows, key=lambda x: x[-1])
    
    # Remove the datetime object from the rows
    for row in sorted_rows:
        row.pop()
    
    # Combine headers and sorted rows
    sorted_data = [headers] + sorted_rows
    
    # Write the sorted data to the output file
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(sorted_data)

input_file = 'utils/trainlogger/userdata/xm9g.csv'
output_file = 'utils/trainlogger/userdata/xm9g.csv'
sortDate(input_file, output_file)
