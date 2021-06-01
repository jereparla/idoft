import sys
import logging
import errorhandler
from tso_iso_checker import run_checks_tso_iso
from tic_fic_checker import run_checks_tic_fic
from pr_checker import run_checks_pr
from utils import log_error

if __name__ == "__main__":
    error_handler = errorhandler.ErrorHandler()
    stream_handler = logging.StreamHandler(stream=sys.stderr)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    log_error.tracker = 0
    run_checks_pr(logger)
    run_checks_tic_fic(logger)
    run_checks_tso_iso(logger)
    if error_handler.fired:
        logger.critical('FAILURE: Exiting with code 1 due to ' +
                        str(log_error.tracker) + ' logged errors.')
        raise SystemExit(1)
    else:
        logger.info('Success: 0 logged errors')