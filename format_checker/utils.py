"""Contains functions and data common to all other modules."""

import re
import subprocess

# Contains regexs for columns that are commmon to pr-data and tic-fic-data
common_data = {
    "Project URL": re.compile(r"(https:\/\/github.com)(\/(\w|\.|-)+){2}"),
    "SHA": re.compile(r"\b[0-9a-f]{40}\b"),
    "Module Path": re.compile(r"((\w|\.|-)+(\/|\w|\.|-)*)|^$"),
    "Fully-Qualified Name": re.compile(
        r"((\w|\s)+\.)+(\w+|\d+|\W+)+(\[((\d+)|(\w+|\s)+)\])?"
    ),
}


def get_commit_list(commit_range):
    """
    Turns the commit range into a useful list of commits (the ones
    contained in the push/PR).
    """

    # If there is no commit range, it must be because the tool is running
    # locally, so get the list of commits from origin/<current-branch> to the
    # last commit made
    if commit_range == []:
        commit_range = (
            subprocess.check_output(
                "git log --oneline origin/"
                + '$(git branch | grep "\\* *" | cut -d " " -f 2)..'
                + '$(git rev-parse --short HEAD) | cut -d " " -f 1',
                shell=True,
            )
            .decode("utf-8")
            .split("\n")[:-1]
        )

    # If it's the first push to a new branch, the event.before commit
    # will consist of 40 zeroes. This needs to be handled separately
    elif re.fullmatch(r"0{40}", commit_range[0]):
        commit_range = [commit_range[1][:7]] + subprocess.check_output(
            "git log --oneline "
            + str(commit_range[1])
            + ".."
            + str(commit_range[2])
            + ' | cut -d " " -f 1',
            shell=True,
        ).decode("utf-8").split("\n")[:-1]
    else:
        commit_range = (
            subprocess.check_output(
                "git log --oneline "
                + str(commit_range[0])
                + ".."
                + str(commit_range[1])
                + ' | cut -d " " -f 1',
                shell=True,
            )
            .decode("utf-8")
            .split("\n")[:-1]
        )
    return commit_range


def get_committed_lines(filename, commit_range):
    """
    Computes which lines have been modified in the commits contained in the
    push/PR.
    """

    commit_list = get_commit_list(commit_range)
    if commit_list != []:
        commit_list = "\\|".join(commit_range)
        command = (
            "git blame "
            + filename
            + " | grep -n '"
            + commit_list
            + "' | cut -f1 -d:"
        )
        committed_lines = subprocess.check_output(command, shell=True)
        committed_lines = committed_lines.decode("utf-8").split("\n")[:-1]
        return committed_lines
    return commit_list


def get_uncommitted_lines(filename):
    """
    Computes which lines have been modified in filename
    but not yet committed.
    """

    command = "git blame " + filename + " | grep -n '^0\\{8\\} ' | cut -f1 -d:"
    uncommitted_lines = subprocess.check_output(command, shell=True)
    uncommitted_lines = uncommitted_lines.decode("utf-8").split("\n")[:-1]
    return uncommitted_lines


def log_info(filename, log, message):
    """Logs a merely informational message."""

    log.info("INFO: On file " + filename + ": " + message)


def log_std_error(filename, log, line, row, key):
    """Logs a standard error."""

    log_std_error.tracker += 1
    log.error(
        "ERROR: On file "
        + filename
        + ", row "
        + str(line + 1)
        + ":\n"
        + "Invalid "
        + key
        + ': "'
        + row[key]
        + '"'
    )


def log_esp_error(filename, log, message):
    """Logs a special error."""

    log_esp_error.tracker += 1
    log.error("ERROR: On file " + filename + ": " + message)


def log_warning(filename, log, line, message):
    """Logs a warning."""

    log_warning.tracker += 1
    log.warning(
        "WARNING: On file "
        + filename
        + ", row "
        + str(line + 1)
        + ": \n"
        + message
    )


def check_header(header, valid_dict, filename, log):
    """Validates that the header is correct."""

    if not header == valid_dict["columns"]:

        # Check that columns are properly formatted
        log_esp_error(filename, log, "The header is improperly formatted")


def check_common_rules(filename, row, i, log):
    """
    Checks validity of Project URL, SHA Detected, Module Path,
    Fully-Qualified Test Name (packageName.ClassName.methodName).
    """

    if not common_data["Project URL"].fullmatch(row["Project URL"]):
        log_std_error(filename, log, i, row, "Project URL")
    if not common_data["SHA"].fullmatch(row["SHA Detected"]):
        log_std_error(filename, log, i, row, "SHA Detected")
    if not common_data["Module Path"].fullmatch(row["Module Path"]):
        log_std_error(filename, log, i, row, "Module Path")
    if not common_data["Fully-Qualified Name"].fullmatch(
        row["Fully-Qualified Test Name (packageName.ClassName.methodName)"]
    ):
        log_std_error(
            filename,
            log,
            i,
            row,
            "Fully-Qualified Test Name (packageName.ClassName.methodName)",
        )


def check_row_length(header_len, filename, row, i, log):
    """Checks that each row has the required length."""

    if len(row) != header_len:
        log_std_error(filename, log, i, "row length", str(row))


def check_sort(filename, log):
    """Checks order of a file."""

    command = (
        'echo "$(head -n1 '
        + filename
        + " && tail +2 "
        + filename
        + ' | LC_ALL=C sort -k1,1 -k4,4 -t, -f)" >  sorted-'
        + filename
        + "; diff "
        + filename
        + " sorted-"
        + filename
        + "; rm sorted-"
        + filename
    )
    diff = subprocess.check_output(command, shell=True).decode("utf-8")
    if diff != "":
        log_esp_error(filename, log, "The file is not properly ordered")
