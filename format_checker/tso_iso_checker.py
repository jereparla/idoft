import csv
import re
from utils import log_std_error, check_header, check_row_length, check_common_rules, common_data

# Contains information and data unique to tso-iso-rates.csv


tso_iso_rates = {
    'columns': [
        'Project URL',
        'SHA Detected',
        'Module Path',
        'Fully-Qualified Test Name (packageName.ClassName.methodName)',
        'Number Of Test Failures In Test Suite',
        'Number Of Test Runs In Test Suite',
        'P-Value',
        'Is P-Value Less Or Greater Than 0.05',
        'Total Runs In Test Suite',
        'Number of Times Test Passed In Test Suite',
        'Total Runs In Isolation',
        'Number of Times Test Passed In Isolation'],
    'Failures/Runs': r'\((\d+\;)+\d+\)',
    'P-Value': r'\d(\.\d+(E-\d+)?)?',
    'Less/Greater': r'(less)|(greater)',
    'Last 4': r'\d+'}

# Checks validity of Total Runs In Test Suite, Number of Times Test Passed
# In Test Suite, Total Runs In Isolation, Number of Times Test Passed In
# Isolation


def check_totals(filename, row, i, log):
    keys = [
        'Total Runs In Test Suite',
        'Number of Times Test Passed In Test Suite',
        'Total Runs In Isolation',
        'Number of Times Test Passed In Isolation']
    for key in keys:
        if not re.fullmatch(tso_iso_rates['Last 4'], row[key]):
            log_std_error(filename, log, i, row, key)
# Checks validity of Is P-Value Less Or Greater Than 0.05


def check_less_greater(filename, row, i, log):
    if not re.fullmatch(
            tso_iso_rates['Less/Greater'],
            row['Is P-Value Less Or Greater Than 0.05']):
        log_std_error(filename, log, i, row, 'Is P-Value Less Or Greater Than 0.05')

# Checks validity of P-Value


def check_pvalue(filename, row, i, log):
    if not re.fullmatch(tso_iso_rates['P-Value'], row['P-Value']):
        log_std_error(filename, log, i, row, 'P-Value')

# Checks validity of Number Of Test Runs In Test Suite


def check_num_runs(filename, row, i, log):
    if not re.fullmatch(
            tso_iso_rates['Failures/Runs'],
            row['Number Of Test Runs In Test Suite']):
        log_std_error(ilename, log, i, row, 'Number Of Test Runs In Test Suite')

# Checks validity of Number Of Test Failures In Test Suite


def check_num_failures(filename, row, i, log):
    if not re.fullmatch(
            tso_iso_rates['Failures/Runs'],
            row['Number Of Test Failures In Test Suite']):
        log_std_error(filename, log, i, row, 'Number Of Test Failures In Test Suite')

# Checks that tso-iso-data.csv is properly formatted.


def run_checks_tso_iso(log):
    file = 'tso-iso-rates.csv'
    with open(file, newline='') as csvfile:
        info = csv.DictReader(csvfile, tso_iso_rates['columns'])
        header = next(info)
        check_header(list(header.keys()), tso_iso_rates, file, log)
        for i, row in enumerate(info):
            i += 2
            params = [file, row, i, log]
            check_row_length(*params, len(header))
            check_num_failures(*params)
            check_num_runs(*params)
            check_pvalue(*params)
            check_less_greater(*params)
            check_totals(*params)
