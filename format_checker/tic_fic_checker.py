import csv
import re
from utils import log_std_error, check_header, check_row_length, check_common_rules, common_data

# Contains information and regexs unique to tic-fic-data.csv


tic_fic_data = {
    'columns': [
        'Project URL',
        'SHA Detected',
        'Module Path',
        'Fully-Qualified Test Name (packageName.ClassName.methodName)',
        'TIC = FIC',
        'Test-Introducing Commit SHA',
        'Test-Introducing Commit Fully-Qualified Test Name',
        'Test-Introducing Commit Module Path',
        'Flakiness-Introducing Commit SHA',
        'Flaky Test File Modified',
        'Other Test Files Modified',
        'Code Under Test Files Modified',
        'Build Related Files Modified',
        'Commits Between TIC-FIC Modifying Flaky Test Class',
        'Commits Between TIC-FIC Modifying Other Test Files',
        'Commits Between TIC-FIC Modifying Code Under Test Files',
        'Commits Between TIC-FIC Modifying Build Related Files',
        'Commits Between TIC-FIC',
        'Days Between TIC-FIC'],
    'TIC = FIC': r'(TRUE)|(FALSE)',
    'Modified': r'(TRUE)|(FALSE)|^$',
    'Commits Between': r'\d+|^$',
    'Days Between TIC-FIC': r'(\d+\.\d+)|^$'}

# Checks validity of Days Between TIC-FIC


def check_days_between(filename, row, i, log):
    if not re.fullmatch(
            tic_fic_data['Days Between TIC-FIC'],
            row['Days Between TIC-FIC']):
        log_std_error(filename, log, i, row, 'Days Between TIC-FIC')

# Checks validity of Flaky Test File Modified, Other Test Files Modified,
# Code Under Test Files Modified, Build Related Files Modified


def check_mods(filename, row, i, log):
    keys = [
        'Flaky Test File Modified',
        'Other Test Files Modified',
        'Code Under Test Files Modified',
        'Build Related Files Modified']
    for key in keys:
        if not re.fullmatch(tic_fic_data['Modified'], row[key]):
            log_std_error(filename, log, i, row, key)

# Checks of Flakiness-Introducing Commit SHA


def check_fic_SHA(filename, row, i, log):
    if not re.fullmatch(
            common_data['SHA'],
            row['Flakiness-Introducing Commit SHA']):
        log_std_error(filename, log, i, row, 'Flakiness-Introducing Commit SHA')

# Checks validity of Test-Introducing Commit Module Path


def check_tic_mp(filename, row, i, log):
    if not re.fullmatch(
            common_data['Module Path'],
            row['Test-Introducing Commit Module Path']):
        log_std_error(ilename, log, i, row, 'Test-Introducing Commit Module Path')

# Checks validity of Test-Introducing Commit Fully-Qualified Test Name


def check_tic_fqn(filename, row, i, log):
    if not re.fullmatch(
            common_data['Fully-Qualified Name'],
            row['Test-Introducing Commit Fully-Qualified Test Name']):
        log_std_error(filename, log, i, row, 'Test-Introducing Commit Fully-Qualified Test Name')

# Checks validity of Test-Introducing Commit SHA


def check_tic_SHA(filename, row, i, log):
    if not re.fullmatch(
            common_data['SHA'],
            row['Test-Introducing Commit SHA']):
        log_std_error(filename, log, i, row, 'Test-Introducing Commit SHA')

# Checks validity of TIC = FIC.


def check_tic_eq_fic(filename, row, i, log):
    if not re.fullmatch(tic_fic_data['TIC = FIC'], row['TIC = FIC']):
        log_std_error(filename, log, i, row, 'TIC = FIC')


# Checks that tic-fic-data.csv is properly formatted.


def run_checks_tic_fic(log):
    file = 'tic-fic-data.csv'
    with open(file, newline='') as csvfile:
        info = csv.DictReader(csvfile, tic_fic_data['columns'])
        header = next(info)
        check_header(list(header.keys()), tic_fic_data, file, log)
        for i, row in enumerate(info):
            i += 2
            params = [file, row, i, log]
            check_row_length(*params, len(header))
            check_common_rules(*params)
            check_tic_eq_fic(*params)
            check_tic_SHA(*params)
            check_tic_fqn(*params)
            check_tic_mp(*params)
            check_fic_SHA(*params)
            check_mods(*params)
            check_days_between(*params)
