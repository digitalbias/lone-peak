#!/usr/bin/env python3

import pandas as pd
import sys

PREPAID_WINTERIZATION_BASE_FEE = 110
PREPAID_WINTERIZATION_PER_ZONE_FEE = 8
PREPAID_BACKFLOW_FEE = 75
MAX_WINTERIZATION_ZONES = 10

def clean_csv(input_file, output_file):
    """Cleans a CSV file by filtering rows, keeping specific columns, inserting new columns, and performing conversions.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
    """

    # Read the CSV file
    df = pd.read_csv(input_file)

    # Filter rows where 'Status' is 'Completed'
    df = df[df['Status'] == 'Completed']

    # Keep only specified columns
    keep_columns = ['Id', 'Date', 'Contact Name', 'Service Address', 'Service Agent', 'Additional Agents', 'Number of Agents', 'Quantity', 'Service/Part Name', 'Total', 'Discount', 'SES Score']
    df = df[keep_columns]

    # Convert 'Date' to datetime format
    # df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y')
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=False)

    # Convert 'Total' to numeric format
    df['Total'] = df['Total'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)

    # Insert new columns between 'Discount' and 'SES Score'
    df.insert(df.columns.get_loc('SES Score'), 'Prepaid', None)
    df.insert(df.columns.get_loc('SES Score'), 'Prepaid+Total', None)

    # Calculate 'Prepaid' based on 'Service/Part Name' and 'Quantity'
    def calculate_prepaid(row):
        if row['Service/Part Name'] == 'Pre-Paid Winterization':
            if row['Quantity'] <= MAX_WINTERIZATION_ZONES:
                return PREPAID_WINTERIZATION_BASE_FEE
            else:
                return (row['Quantity'] - MAX_WINTERIZATION_ZONES) * PREPAID_WINTERIZATION_PER_ZONE_FEE + PREPAID_WINTERIZATION_BASE_FEE
        elif row['Service/Part Name'] == 'Prepaid Backflow':
            return PREPAID_BACKFLOW_FEE
        else:
            return 0

    df['Prepaid'] = df.apply(calculate_prepaid, axis=1)
    df['Prepaid+Total'] = df['Prepaid'] + df['Total']

    # Format the 'Date' column as MM/DD/YY
    df['Date'] = df['Date'].dt.strftime('%m/%d/%y')

    # Write the cleaned data to a new CSV file
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_csv.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    clean_csv(input_file, output_file)

