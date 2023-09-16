import os
import json
import csv
import re
import logging
import time
from tqdm import tqdm

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def load(filepath):
    filenames = []
    try:
        files = os.listdir(filepath)
        for file in files:
            if os.path.isfile(os.path.join(filepath, file)):
                filenames.append(os.path.join(filepath, file))
        return filenames
    except FileNotFoundError:
        logging.error(f"Directory not found: {filepath}")
        print(f"Directory not found: {filepath}")
        return []

def readNmatchFile(filename, key, options):
    try:
        matching_results = []

        if filename.endswith(".json"):
            with open(filename, 'r') as file:
                data = json.load(file)
                logging.info(f"Searching in JSON file: {filename}")
                for item in data:
                    if re.search(key, json.dumps(item, indent=4), re.IGNORECASE if options["case_insensitive"] else 0):
                        matching_results.append(item)
                        print(item)  # Print the matching item
        elif filename.endswith(".csv"):
            with open(filename, 'r') as file:
                csv_reader = csv.reader(file)
                logging.info(f"Searching in CSV file: {filename}")
                header_printed = False
                for row in csv_reader:
                    if not header_printed:
                        matching_results.append(row)  # Add the header
                        header_printed = True
                    for cell in row:
                        if re.search(key, cell, re.IGNORECASE if options["case_insensitive"] else 0):
                            matching_results.append(row)
                            print(row)  # Print the matching row
        else:
            with open(filename, 'r') as file:
                logging.info(f"Searching in TXT file: {filename}")
                for line in file:
                    if re.search(key, line, re.IGNORECASE if options["case_insensitive"] else 0):
                        matching_results.append(line.strip())
                        print(line.strip())  # Print the matching line

        return matching_results

    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        print(f"File not found: {filename}")
        return []


def write_to_output_file(data, options):
    timestamp = time.strftime("%Y%m%d%H%M%S")
    if options["output_format"] == "json":
        output_file = f"search_results_{timestamp}.json"
        with open(output_file, 'w') as json_output_file:
            json.dump(data, json_output_file, indent=4)
    else:
        output_file = f"search_results_{timestamp}.txt"
        with open(output_file, 'w') as text_output_file:
            for item in data:
                text_output_file.write(str(item) + "\n")

def queryByString(filepath, key, options):
    log_file = "search_log.txt"
    setup_logging(log_file)

    files_to_search = load(filepath)
    if not files_to_search:
        return

    # Create a list to store matching lines or items
    search_results = []

    total_files = len(files_to_search)
    progress_bar = tqdm(total=total_files, desc="Files Processed", unit="file")

    for filename in files_to_search:
        search_results += readNmatchFile(filename, key, options)
        progress_bar.update(1)

    progress_bar.close()

    # Write all matching lines or items to the output file
    write_to_output_file(search_results, options)


# Example usage:
# options = {
#     "case_insensitive": True,
#     "output_format": "json",  # Choose "json" or "txt"
#     "log_file": "search.log",
# }
# queryByString("/path/to/your/directory", "search_keyword", options)

import sys

def calculateMean(filepath, device, column_name, options, condition=None, timestamp=None):
    log_file = "mean_calculation_log.txt"
    setup_logging(log_file)

    files_to_search = load(filepath)
    if not files_to_search:
        return

    total_values = []  # Collect all values from all files
    console_output = []  # Collect console output

    for filename in files_to_search:
        try:
            if filename.endswith(".csv"):
                with open(filename, 'r') as file:
                    csv_reader = csv.reader(file)
                    logging.info(f"Calculating mean from CSV file: {filename}")
                    header = next(csv_reader)
                    if column_name in header:
                        column_index = header.index(column_name)
                        file_values = []  # Values for this file
                        for row in csv_reader:
                            if row[1] == device:  # Check the "device" column
                                try:
                                    value = float(row[column_index])
                                    if condition is None or evaluate_condition(value, condition):
                                        file_values.append(value)
                                        total_values.append(value)
                                        if timestamp and row[0] == timestamp:
                                            console_output.append(f"Found matching record in {filename}: {row}")
                                            print(f"Found matching record in {filename}: {row}")  # Print to console
                                except (ValueError, IndexError):
                                    continue
                        if file_values:
                            file_mean = sum(file_values) / len(file_values)
                            logging.info(f"Mean value calculated for {filename}: {file_mean}")
                            console_output.append(f"Mean value calculated for {filename}: {file_mean}")
                            print(f"Mean value calculated for {filename}: {file_mean}")  # Print to console
                    else:
                        logging.warning(f"Column '{column_name}' not found in CSV file: {filename}")
            elif filename.endswith(".json"):
                with open(filename, 'r') as file:
                    data = json.load(file)
                    logging.info(f"Calculating mean from JSON file: {filename}")
                    file_values = []  # Values for this file
                    for item in data:
                        if item["device"] == device:  # Check the "device" key
                            try:
                                value = float(item[column_name])
                                if condition is None or evaluate_condition(value, condition):
                                    file_values.append(value)
                                    total_values.append(value)
                                    if timestamp and item["timestamp"] == timestamp:
                                        console_output.append(f"Found matching record in {filename}: {item}")
                                        print(f"Found matching record in {filename}: {item}")  # Print to console
                            except (ValueError, KeyError):
                                continue
                    if file_values:
                        file_mean = sum(file_values) / len(file_values)
                        logging.info(f"Mean value calculated for {filename}: {file_mean}")
                        console_output.append(f"Mean value calculated for {filename}: {file_mean}")
                        print(f"Mean value calculated for {filename}: {file_mean}")  # Print to console
            elif filename.endswith(".txt"):
                with open(filename, 'r') as file:
                    logging.info(f"Calculating mean from TXT file: {filename}")
                    file_values = []  # Values for this file
                    for line in file:
                        parts = line.strip().split()
                        if len(parts) >= 3 and parts[0] == device and parts[1] == column_name:
                            try:
                                value = float(parts[2])
                                if condition is None or evaluate_condition(value, condition):
                                    file_values.append(value)
                                    total_values.append(value)
                                    if timestamp and parts[3] == timestamp:
                                        console_output.append(f"Found matching record in {filename}: {line.strip()}")
                                        print(f"Found matching record in {filename}: {line.strip()}")  # Print to console
                            except (ValueError, IndexError):
                                continue
                    if file_values:
                        file_mean = sum(file_values) / len(file_values)
                        logging.info(f"Mean value calculated for {filename}: {file_mean}")
                        console_output.append(f"Mean value calculated for {filename}: {file_mean}")
                        print(f"Mean value calculated for {filename}: {file_mean}")  # Print to console
            else:
                logging.error(f"Unsupported file format: {filename}")
        except FileNotFoundError:
            logging.error(f"File not found: {filename}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    if total_values:
        total_mean = sum(total_values) / len(total_values)
        logging.info(f"Final total mean value calculated: {total_mean}")
        console_output.append(f"Final total mean value calculated: {total_mean}")
        print(f"Final total mean value calculated: {total_mean}")  # Print to console
        output_mean = f"Final total mean value calculated for {device} {column_name}: {total_mean}\n"
        return total_mean
    else:
        logging.info("No valid values found for mean calculation.")
        console_output.append("No valid values found for mean calculation.")
        print("No valid values found for mean calculation.")  # Print to console

    # Save console output to a separate file
    timestamp = time.strftime("%Y%m%d%H%M%S")
    console_output_file = f"mean_calculation_results{timestamp}.txt"
    with open(console_output_file, 'w') as text_output_file:
        text_output_file.writelines([f"{line}\n" for line in console_output])
    

def evaluate_condition(value, condition):
    if condition is None:
        return True
    operator = condition[0]
    threshold = float(condition[1:])
    if operator == "=":
        return value == threshold
    elif operator == ">":
        return value > threshold
    elif operator == "<":
        return value < threshold
    else:
        return False






