#!/usr/bin/env python3

import pandas as pd
import sys

# Get input and output filenames from command-line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# Read the CSV file
df = pd.read_csv(input_file)

# Convert the "date" column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=False)

# Remove the '$' symbol and commas from the "Prepaid+Total" column, only if they exist
df['Prepaid+Total'] = df['Prepaid+Total'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)

# Convert the column to numeric format
df['Prepaid+Total'] = pd.to_numeric(df['Prepaid+Total'])

# Sort the DataFrame
df.sort_values(by=['Date', 'Service Agent', 'Additional Agents'], inplace=True)

# Group by relevant columns, ignoring blank "Additional Agents" and round the sum
grouped_df = df.groupby(['Date', 'Service Agent', df['Additional Agents'].fillna('').astype(str)]).agg({'Prepaid+Total': lambda x: round(x.sum(), 2)})

# Reset the index to make grouped columns regular columns
grouped_df.reset_index(inplace=True)

# Create a sorting key column
df['sort_key'] = df['Date'].astype(str) + df['Service Agent'] + df['Additional Agents'].fillna('')
grouped_df['sort_key'] = grouped_df['Date'].astype(str) + grouped_df['Service Agent'] + grouped_df['Additional Agents'].fillna('') + 'summary'

# Concatenate the original and grouped DataFrames, appending grouped_df to the end
combined_df = pd.concat([df, grouped_df], ignore_index=True)

# Sort the combined DataFrame by the 'sort_key' column
combined_df.sort_values(by='sort_key', inplace=True)

# Set 'Date', 'Service Agent', and 'Additional Agent' to blank for summary rows
combined_df.loc[combined_df['sort_key'].str.endswith('summary'), ['Date', 'Service Agent', 'Additional Agents']] = ''

# Insert a blank row after each summary row
combined_df = combined_df.reindex(combined_df.index.repeat(2)).fillna('')
combined_df.iloc[1::2] = ''

# Drop the 'sort_key' column
combined_df.drop('sort_key', axis=1, inplace=True)

# Format the 'Date' column as MM/DD/YY
combined_df['Date'] = combined_df['Date'].dt.strftime('%m/%d/%y')

# Write the DataFrame to the specified output CSV file
combined_df.to_csv(output_file, index=False)
