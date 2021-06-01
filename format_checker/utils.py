import re
import csv

# Contains regexs for columns that are commmon to pr-data and tic-fic-data


common_data = {
    'Project URL': r'(https:\/\/github.com)(\/(\w|\.|-)+){2}',  # USE COMPILE
    'SHA': r'\b[0-9a-f]{40}\b',
    'Module Path': r'((\w|\.|-)+(\/|\w|\.|-)*)|^$',
    'Fully-Qualified Name': r'((\w|\s)+\.)+(\w+|\d+|\W+)+(\[((\d+)|(\w+|\s)+)\])?'
}

# Logs an error


def log_error(filename, line, row, key, log):
    log_error.tracker += 1
    log.error("ERROR: On file " + filename + ", row " + str(line) +
              ":\n" + "Invalid " + key + ": \"" + row[key] + "\"")

# Validates that the header is correct


def check_header(header, valid_dict, filename, log):
    if not header == valid_dict['columns']:
        # Check that columns are properly formatted
        log_error(filename, 1, 'header', str(header), log)

# Checks validity of Project URL, SHA Detected, Module Path,
# Fully-Qualified Test Name (packageName.ClassName.methodName)


def check_common_rules(filename, row, i, log):
    if not re.fullmatch(common_data['Project URL'], row['Project URL']):
        log_error(filename, i, row, 'Project URL', log)
    if not re.fullmatch(common_data['SHA'], row['SHA Detected']):
        log_error(filename, i, row, 'SHA Detected', log)
    if not re.fullmatch(common_data['Module Path'], row['Module Path']):
        log_error(filename, i, row, 'Module Path', log)
    if not re.fullmatch(
            common_data['Fully-Qualified Name'],
            row['Fully-Qualified Test Name (packageName.ClassName.methodName)']):
        log_error(
            filename,
            i,
            row,
            'Fully-Qualified Test Name (packageName.ClassName.methodName)',
            log)


# Checks that each row has the required length

def check_row_length(filename, row, i, log, header_len):
    if len(row) != header_len:
        log_error(filename, i, 'row length', str(row), log)
