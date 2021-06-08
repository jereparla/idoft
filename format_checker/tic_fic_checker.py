import csv
import re
from utils import (
    log_std_error,
    log_info,
    check_header,
    check_row_length,
    check_common_rules,
    common_data,
    get_committed_lines,
    get_uncommitted_lines,
)

# Contains information and regexs unique to tic-fic-data.csv
tic_fic_data = {
    "columns": [
        "Project URL",
        "SHA Detected",
        "Module Path",
        "Fully-Qualified Test Name (packageName.ClassName.methodName)",
        "TIC = FIC",
        "Test-Introducing Commit SHA",
        "Test-Introducing Commit Fully-Qualified Test Name",
        "Test-Introducing Commit Module Path",
        "Flakiness-Introducing Commit SHA",
        "Flaky Test File Modified",
        "Other Test Files Modified",
        "Code Under Test Files Modified",
        "Build Related Files Modified",
        "Commits Between TIC-FIC Modifying Flaky Test Class",
        "Commits Between TIC-FIC Modifying Other Test Files",
        "Commits Between TIC-FIC Modifying Code Under Test Files",
        "Commits Between TIC-FIC Modifying Build Related Files",
        "Commits Between TIC-FIC",
        "Days Between TIC-FIC",
    ],
    "TIC = FIC": re.compile(r"(TRUE)|(FALSE)"),
    "Modified": re.compile(r"(TRUE)|(FALSE)|^$"),
    "Commits Between": re.compile(r"\d+|^$"),
    "Days Between TIC-FIC": re.compile(r"(\d+\.\d+)|^$"),
}


# Checks validity of Days Between TIC-FIC
def check_days_between(filename, row, i, log):
    if not tic_fic_data["Days Between TIC-FIC"].fullmatch(
        row["Days Between TIC-FIC"]
    ):
        log_std_error(filename, log, i, row, "Days Between TIC-FIC")


# Checks validity of Flaky Test File Modified, Other Test Files Modified,
# Code Under Test Files Modified and Build Related Files Modified
def check_mods(filename, row, i, log):
    keys = [
        "Flaky Test File Modified",
        "Other Test Files Modified",
        "Code Under Test Files Modified",
        "Build Related Files Modified",
    ]
    for key in keys:
        if not tic_fic_data["Modified"].fullmatch(row[key]):
            log_std_error(filename, log, i, row, key)


# Checks of Flakiness-Introducing Commit SHA
def check_fic_sha(filename, row, i, log):
    if not common_data["SHA"].fullmatch(
        row["Flakiness-Introducing Commit SHA"]
    ):
        log_std_error(
            filename, log, i, row, "Flakiness-Introducing Commit SHA"
        )


# Checks validity of Test-Introducing Commit Module Path
def check_tic_mp(filename, row, i, log):
    if not common_data["Module Path"].fullmatch(
        row["Test-Introducing Commit Module Path"]
    ):
        log_std_error(
            filename, log, i, row, "Test-Introducing Commit Module Path"
        )


# Checks validity of Test-Introducing Commit Fully-Qualified Test Name
def check_tic_fqn(filename, row, i, log):
    if not common_data["Fully-Qualified Name"].fullmatch(
        row["Test-Introducing Commit Fully-Qualified Test Name"]
    ):
        log_std_error(
            filename,
            log,
            i,
            row,
            "Test-Introducing Commit Fully-Qualified Test Name",
        )


# Checks validity of Test-Introducing Commit SHA
def check_tic_sha(filename, row, i, log):
    if not common_data["SHA"].fullmatch(row["Test-Introducing Commit SHA"]):
        log_std_error(filename, log, i, row, "Test-Introducing Commit SHA")


# Checks validity of TIC = FIC.
def check_tic_eq_fic(filename, row, i, log):
    if not tic_fic_data["TIC = FIC"].fullmatch(row["TIC = FIC"]):
        log_std_error(filename, log, i, row, "TIC = FIC")


# Checks that tic-fic-data.csv is properly formatted.
def run_checks_tic_fic(log, commit_range):
    file = "tic-fic-data.csv"
    committed_lines = get_committed_lines(file, commit_range)
    uncommitted_lines = get_uncommitted_lines(file)
    with open(file, newline="") as csvfile:
        info = csv.DictReader(csvfile, tic_fic_data["columns"])
        header = next(info)
        if "1" in uncommitted_lines:
            check_header(list(header.values()), tic_fic_data, file, log)
        if uncommitted_lines != [] or committed_lines != []:
            for i, row in enumerate(info):
                i += 2
                line = str(i)
                if (line in uncommitted_lines) or (line in committed_lines):
                    params = [file, row, i, log]
                    check_row_length(len(header), *params)
                    check_common_rules(*params)
                    check_tic_eq_fic(*params)
                    check_tic_sha(*params)
                    check_tic_fqn(*params)
                    check_tic_mp(*params)
                    check_fic_sha(*params)
                    check_mods(*params)
                    check_days_between(*params)
        else:
            log_info(file, log, "There are no changes to be checked")
