import csv
import re
from utils import log_error, check_header, check_row_length, check_common_rules, common_data

# Contains information and regexs unique to pr-data.csv


pr_data = {
    'columns': ['Project URL', 'SHA Detected', 'Module Path',
                'Fully-Qualified Test Name (packageName.ClassName.methodName)', 'Category', 'Status', 'PR Link', 'Notes'],
    'Category': ['OD', 'OD-Brit', 'OD-Vic', 'ID', 'NOD', 'NDOD', 'NDOI', 'NDOI', 'UD'],
    'Status': ['', 'Opened', 'Accepted', 'InspiredAFix', 'DeveloperFixed', 'Deleted', 'Rejected', 'Skipped'],
    'PR Link': r'((https:\/\/github.com\/((\w|\.|-)+\/)+)(pull\/\d+))',
    'Notes': r'(https:\/\/github.com\/TestingResearchIllinois\/((idoft)|(flaky-test-dataset))\/issues\/\d+)|^$'
}

# Check validity of Category


def check_category(filename, row, i, log):
    if not re.fullmatch(
            r'(\w+|-|\;)*\w+',
            row['Category']) or not all(
            x in pr_data['Category'] for x in row['Category'].split(';')):
        log_error(filename, i, row, 'Category', log)

# Check validity of Status


def check_status(filename, row, i, log):
    if not row['Status'] in pr_data['Status']:
        log_error(filename, i, row, 'Status', log)

# Check that the status is consistent with the requirements


def check_status_consistency(filename, row, i, log):
    # Checks validity if Status is one of Accepted, Opened, Rejected
    if row['Status'] in ['Accepted', 'Opened', 'Rejected']:
        # If it is, check that it has a valid PR Link
        if not re.fullmatch(
            pr_data['PR Link'],
            row['PR Link']) or (
            re.sub(
                r'\/pull\/\d+',
                '',
                row['PR Link']).casefold() != row['Project URL'].casefold()):
            log_error(filename, i, row, 'PR Link', log)

    if row['Status'] in ['InspiredAFix', 'Skipped']:

        # Must contain a note

        if row['Notes'] == '':
            log_error(filename, i, row, 'Notes', log)

        # Must contain a PR Link

        if row['Status'] == 'InspiredAFix' and not re.fullmatch(
                pr_data['PR Link'], row['PR Link']):
            log_error(filename, i, row, 'PR Link', log)

# Checks validity of Notes


def check_notes(filename, row, i, log):
    if not re.fullmatch(pr_data['Notes'], row['Notes']):
        log_error(filename, i, row, 'Notes', log)


# Checks that pr-data.csv is properly formatted.


def run_checks_pr(log):
    file = 'pr-data.csv'
    with open(file, newline='') as csvfile:
        info = csv.DictReader(csvfile, pr_data['columns'])
        header = next(info)
        check_header(list(header.keys()), pr_data, file, log)
        for i, row in enumerate(info):
            i += 2
            params = [file, row, i, log]
            check_row_length(*params, len(header))
            check_common_rules(*params)
            check_category(*params)
            check_status(*params)
            check_status_consistency(*params)
            check_notes(*params)
