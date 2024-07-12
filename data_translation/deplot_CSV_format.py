import pandas as pd
import glob
import os
import sys

# Define functions for processing
def string_to_dataframe_and_title(data_string, filepath):
    ''' Convert a string representation of table data into a DataFrame and extract title if it exists. '''
    rows = data_string.strip().split("<0x0A>")
    
    title = None
    header = None

    # Check and extract title if it exists
    if "TITLE |" in rows[0]:
        potential_title = rows[0].split(" | ", 1)[1]
        if potential_title.strip().lower() not in ['', 'title']:
            title = potential_title
        rows.pop(0)

    # Extract header
    if rows:
        header = [h.strip() for h in rows.pop(0).split("|") if h.strip()]
    else:
        raise ValueError("No header row found after the title row.")

    # Check for data rows
    if not rows:
        raise ValueError("No data rows found after the header row.")

    # Process data rows
    records = []
    for row in rows:
        record = [r.strip() for r in row.strip().split("|") if r.strip()]
        if len(record) != len(header):
            print(f"File: {filepath}: Row has {len(record)} columns, expected {len(header)} - row data: {record}")
            return None, title  # to keep original CSV instead
        records.append(record)

    # Create DataFrame and convert numeric values
    df = pd.DataFrame(records, columns=header)
    df = df.apply(pd.to_numeric, errors='coerce')

    return df, title

def save_title_to_file(title, filepath):
    ''' Save extracted title to a text file. '''
    if title:
        title_filepath = f"{filepath.rsplit('.', 1)[0]}-title.txt"
        with open(title_filepath, 'w') as f:
            f.write(title)

def test_csv_conversion(directory_pattern):
    ''' Test CSV conversion by checking for empty DataFrames. '''
    not_converted_properly = []

    for filepath in glob.glob(directory_pattern, recursive=True):
        if filepath.endswith('-dp.csv'):
            try:
                df = pd.read_csv(filepath)
                if df.shape == (0, 1):
                    not_converted_properly.append(filepath)
            except Exception as e:
                not_converted_properly.append(filepath)

    return not_converted_properly

def main(src, dst):
    # Ensure destination directory exists
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    # Pattern for matching CSVs in FigureQA and PlotQA
    data_pattern = os.path.join(src, '**', '*-dp.csv')

    # Process each file matching the pattern
    for filepath in glob.glob(data_pattern, recursive=True):
        with open(filepath, 'r') as file:
            data_string = file.read()

        try:
            result = string_to_dataframe_and_title(data_string, filepath)
            if result is None:
                print(f"Skipping conversion for {filepath} because it removes data.")
                continue

            df, title = result

            if df is not None:
                # Save the DataFrame (overwrite original file)
                df.to_csv(filepath, index=False)
                save_title_to_file(title, filepath)
                print(f"Preprocessing successful for {filepath}")
        except ValueError as e:
            print(f"Error processing {filepath}: {e}")

    # Check for files not converted properly
    csvs_not_converted_properly = test_csv_conversion(data_pattern)
    if csvs_not_converted_properly:
        print(f"CSV files not converted properly: {csvs_not_converted_properly}")
        print(f"Number of CSVs not converted properly: {len(csvs_not_converted_properly)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python format_tables.py <from_path> <to_path>") # Indicate correct usage if wrong command line arguments
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    main(src, dst)
    print("CSV files formatted successfully.")
