import re
import csv
import pandas as pd

# Contains regexs for columns that are commmon to pr-data and tic-fic-data


common_data = {
    'Project URL': r'(https:\/\/github.com)(\/(\w|\.|-)+){2}',  # USE COMPILE
    'SHA': r'\b[0-9a-f]{40}\b',
    'Module Path': r'((\w|\.|-)+(\/|\w|\.|-)*)|^$',
    'Fully-Qualified Name': r'((\w|\s)+\.)+(\w+|\d+|\W+)+(\[((\d+)|(\w+|\s)+)\])?'
}

# Logs a standard error

def log_std_error(filename, log, line, row, key):
    log_std_error.tracker += 1
    log.error("ERROR: On file " + filename + ", row " + str(line) +
            ":\n" + "Invalid " + key + ": \"" + row[key] + "\"")

# Logs a special error


def log_esp_error(filename, log, message):
    log_esp_error.tracker += 1
    log.error("ERROR: On file " + filename + ": " + message)

# Validates that the header is correct


def check_header(header, valid_dict, filename, log):
    if not header == valid_dict['columns']:
        # Check that columns are properly formatted
        log_esp_error(filename, log, "The header is improperly formatted")

# Checks validity of Project URL, SHA Detected, Module Path,
# Fully-Qualified Test Name (packageName.ClassName.methodName)


def check_common_rules(filename, row, i, log):
    if not re.fullmatch(common_data['Project URL'], row['Project URL']):
        log_std_error(filename, log, i, row, 'Project URL')
    if not re.fullmatch(common_data['SHA'], row['SHA Detected']):
        log_std_error(filename, log, i, row, 'SHA Detected')
    if not re.fullmatch(common_data['Module Path'], row['Module Path']):
        log_std_error(filename, log, i, row, 'Module Path')
    if not re.fullmatch(
            common_data['Fully-Qualified Name'],
            row['Fully-Qualified Test Name (packageName.ClassName.methodName)']):
        log_std_error(filename, log, i, row, 'Fully-Qualified Test Name (packageName.ClassName.methodName)')

# Checks that each row has the required length


def check_row_length(filename, row, i, log, header_len):
    if len(row) != header_len:
        log_std_error(filename, log, i, 'row length', str(row))

# Check that the file is well-ordered


def check_sort(filename, sortby, log):
    df = pd.read_csv(filename)
    #sorteddf = df.sort_values(by=sortby, key=lambda col: col.str.lower(), ignore_index = True)
    #print(df.compare(sorteddf))
    #sorteddf.to_csv('sorted-pr-data.csv', index=False)
    if not df.equals(df.sort_values(by=sortby, key=lambda col: col.str.lower(), ignore_index = True)):
        log_esp_error(filename, log, "The file is not properly ordered")
    



