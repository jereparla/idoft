"""Implements rule checks for the pr-data.csv file."""

import csv
import re
from utils import (
    log_std_error,
    log_info,
    log_warning,
    check_header,
    check_row_length,
    check_common_rules,
    get_committed_lines,
    get_uncommitted_lines,
    check_sort,
)

# Contains information and regexs unique to pr-data.csv
pr_data = {
    "columns": [
        "Project URL",
        "SHA Detected",
        "Module Path",
        "Fully-Qualified Test Name (packageName.ClassName.methodName)",
        "Category",
        "Status",
        "PR Link",
        "Notes",
    ],
    "Category": [
        "OD",
        "OD-Brit",
        "OD-Vic",
        "ID",
        "NOD",
        "NDOD",
        "NDOI",
        "NDOI",
        "UD",
    ],
    "Status": [
        "",
        "Opened",
        "Accepted",
        "InspiredAFix",
        "DeveloperFixed",
        "Deleted",
        "Rejected",
        "Skipped",
    ],
    "PR Link": re.compile(
        r"((https:\/\/github.com\/((\w|\.|-)+\/)+)(pull\/\d+))"
    ),
    "Notes": re.compile(
        r"(https:\/\/github.com\/TestingResearchIllinois\/"
        r"((idoft)|(flaky-test-dataset))\\/issues\\/\\d+)|^$"
    ),
}


def check_category(filename, row, i, log):
    """Check validity of Category."""

    if not re.fullmatch(r"(\w+|-|\;)*\w+", row["Category"]) or not all(
        x in pr_data["Category"] for x in row["Category"].split(";")
    ):
        log_std_error(filename, log, i, row, "Category")


def check_status(filename, row, i, log):
    """Check validity of Status."""

    if not row["Status"] in pr_data["Status"]:
        log_std_error(filename, log, i, row, "Status")


def check_status_consistency(filename, row, i, log):
    """Check that the status is consistent with the requirements."""

    # Checks if Status is one of Accepted, Opened, Rejected
    # and checks for required information if so
    if row["Status"] in ["Accepted", "Opened", "Rejected"]:

        # If it is, check that it has a valid PR Link
        if not pr_data["PR Link"].fullmatch(row["PR Link"]) or (
            re.sub(r"\/pull\/\d+", "", row["PR Link"]).casefold()
            != row["Project URL"].casefold()
        ):

            # The project apache/incubator-dubbo was renamed to apache/dubbo,
            # so the Project URL name (old) doesn't match the PR Link name
            # (new), despite them being the same project. This if statement is
            # a workaround for that issue.
            if (
                row["Project URL"]
                == "https://github.com/apache/incubator-dubbo"
                and re.sub(r"\/pull\/\d+", "", row["PR Link"]).casefold()
                == "https://github.com/apache/dubbo"
            ):
                pass
            else:
                log_std_error(filename, log, i, row, "PR Link")

    if row["Status"] in ["InspiredAFix", "Skipped"]:

        # Should contain a note
        if row["Notes"] == "":
            log_warning(
                filename,
                log,
                i,
                "Status " + row["Status"] + " should contain a note",
            )

        # Should contain a PR Link
        if row["Status"] == "InspiredAFix" and not pr_data[
            "PR Link"
        ].fullmatch(row["PR Link"]):
            log_warning(
                filename,
                log,
                i,
                "Status " + row["Status"] + " should have a PR Link",
            )


def check_notes(filename, row, i, log):
    """Checks validity of Notes."""

    if not pr_data["Notes"].fullmatch(row["Notes"]):
        log_std_error(filename, log, i, row, "Notes")


def check_pr_link(filename, row, i, log):
    """Checks validity of the PR Link."""

    if not pr_data["PR Link"].fullmatch(row["PR Link"]):
        log_std_error(filename, log, i, row, "PR Link")


def run_checks_pr(log, commit_range):
    """Checks that pr-data.csv is properly formatted."""

    file = "pr-data.csv"
    committed_lines = get_committed_lines(file, commit_range)
    uncommitted_lines = get_uncommitted_lines(file)
    with open(file, newline="") as csvfile:
        info = csv.DictReader(csvfile, pr_data["columns"])
        header = next(info)
        if "1" in uncommitted_lines:
            check_header(list(header.values()), pr_data, file, log)
        if uncommitted_lines != [] or committed_lines != []:
            for i, row in enumerate(info):
                i += 2
                line = str(i)

                # The line is either:
                # (1) only uncommitted (needs to always bechecked locally),
                # (2) only committed (needs to always be checked in CI) or
                # (3) both in the unpushed commits and uncommitted (which in
                # practice is the same as (1) --the committed one is
                # deprecated--)
                if (line in uncommitted_lines) or (line in committed_lines):
                    params = [file, row, i, log]
                    check_row_length(len(header), *params)
                    check_common_rules(*params)
                    check_category(*params)
                    check_status(*params)
                    check_status_consistency(*params)
                    check_pr_link(*params)
                    check_notes(*params)
            check_sort(file, log)
        else:
            log_info(file, log, "There are no changes to be checked")
