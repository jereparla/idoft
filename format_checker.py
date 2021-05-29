import csv 
import sys
import re 
import logging
import errorhandler

common_data = {
	'Project URL': r'(https:\/\/github.com)(\/(\w|\.|-)+){2}',
	'SHA': r'\b[0-9a-f]{40}\b',
	'Module path': r'((\w|\.|-)+(\/|\w|\.|-)*)|^$',
	'Fully-Qualified': r'((\w)+\.)+(\w+)+' # The whitespace is because https://github.com/pinterest/secor had a whitespace in it --not sure if valid
}

pr_data = {
	'columns': ['Project URL', 'SHA Detected', 'Module Path', 
	'Fully-Qualified Test Name (packageName.ClassName.methodName)', 'Category', 'Status', 'PR Link', 'Notes'],
	'Category': ['OD', 'OD-Brit', 'OD-Vic', 'ID', 'NOD', 'NDOD', 'NDOI', 'NDOI', 'UD'],
	'Status': ['', 'Opened', 'Accepted', 'InspiredAFix', 'DeveloperFixed', 'Deleted', 'Rejected', 'Skipped'],
	'PR Link': r'((https:\/\/github.com\/((\w|\.|-)+\/)+)(pull\/\d+))',
	'Notes': r'(https:\/\/github.com\/TestingResearchIllinois\/((idoft)|(flaky-test-dataset))\/issues\/\d+)|^$'
}

tic_fic_data = {
	'columns': ['Project URL', 'SHA Detected', 'Module Path', 'Fully-Qualified Test Name (packageName.ClassName.methodName)', 
	'TIC = FIC', 'Test-Introducing Commit SHA', 'Test-Introducing Commit Fully-Qualified Test Name', 'Test-Introducing Commit Module Path', 
	'Flakiness-Introducing Commit SHA', 'Flaky Test File Modified', 'Other Test Files Modified', 'Code Under Test Files Modified', 'Build Related Files Modified', 
	'Commits Between TIC-FIC Modifying Flaky Test Class', 'Commits Between TIC-FIC Modifying Other Test Files', 'Commits Between TIC-FIC Modifying Code Under Test Files', 
	'Commits Between TIC-FIC Modifying Build Related Files', 'Commits Between TIC-FIC', 'Days Between TIC-FIC'],
	'TIC = FIC': r'(TRUE)|(FALSE)',
	'Modified': r'(TRUE)|(FALSE)|^$',
	'Commits Between': r'\d+|^$',
	'Days Between TIC-FIC': r'(\d+\.\d+)|^$'
}

tso_iso_rates = {
	'columns': ['Project URL', 'SHA Detected', 'Module Path', 'Fully-Qualified Test Name (packageName.ClassName.methodName)', 
	'Number Of Test Failures In Test Suite', 'Number Of Test Runs In Test Suite', 'P-Value', 'Is P-Value Less Or Greater Than 0.05', 
	'Total Runs In Test Suite', 'Number of Times Test Passed In Test Suite', 'Total Runs In Isolation', 'Number of Times Test Passed In Isolation'],
	'Failures/Runs': r'\((\d+\;)+\d+\)',
	'P-Value': r'\d(\.\d+(E-\d+)?)?',
	'Less/Greater': r'(less)|(greater)',
	'Last 4': r'\d+'
}

def info_message(filename, line, column, mismatch):
	return "ERROR:On file " + filename + ", row " + str(line) + ":\n" + "Invalid " + column + ": " + mismatch

def validate_header(header, valid_dict, filename, log):
	if not header == valid_dict['columns']:
		log.error(info_message(filename, 1, 'header', str(header))) # Check that columns are properly formatted

def validate_common_rules(row, i, filename, header, log):
	keys = common_data.keys() 
	for j, key in enumerate(keys):
		if not re.match(common_data[key], row[j]):
			log.error(info_message(filename, i, header[j], row[j])) # Check repo addresses are valid

def run_checks_tso_iso(log):
	filename = 'tso-iso-rates.csv'
	with open(filename, newline = '') as csvfile:
		info = csv.reader(csvfile)
		header = next(info)
		validate_header(header, tso_iso_rates, filename, log)
		for i, row in enumerate(info):
			i += 2
			if not re.match(tso_iso_rates['Failures/Runs'], row[4]):
			    log.error(info_message(filename, i, header[4], row[4]))
			if not re.match(tso_iso_rates['Failures/Runs'], row[5]):
			    log.error(info_message(filename, i, header[5], row[5]))
			if not re.match(tso_iso_rates['P-Value'], row[6]):
				log.error(info_message(filename, i, header[6], row[6]))
			if not re.match(tso_iso_rates['Less/Greater'], row[7]):
				log.error(info_message(filename, i, header[7], row[7]))
			for j in range(8, 12):
				if not re.match(tso_iso_rates['Last 4'], row[j]):
					log.error(info_message(filename, header[j], row[j]))

def run_checks_tic_fic(log):
	filename = 'tic-fic-data.csv'
	with open(filename, newline = '') as csvfile:
		info = csv.reader(csvfile)
		header = next(info)
		validate_header(header, tic_fic_data, filename, log)
		for i, row in enumerate(info):
			i += 2
			validate_common_rules(row, i, filename, header, log)
			if not re.match(tic_fic_data['TIC = FIC'], row[4]):
				log.error(info_message(filename, i, header[4], row[4]))
			if not re.match(common_data['SHA'], row[5]):
				log.error(info_message(filename, i, header[5], row[5]))
			if not re.match(common_data['Fully-Qualified'], row[6]):
				log.error(info_message(filename, i, header[6], row[6]))
			if not re.match(common_data['Module path'], row[7]): 
			    log.error(info_message(filename, i, header[7], row[7]))
			if not re.match(common_data['SHA'], row[8]):
				log.error(info_message(filename, i, header[8], row[8]))
			for j in range(9, 13):
				if not re.match(tic_fic_data['Modified'], row[j]):
					log.error(info_message(filename, i, header[j], row[j]))
			for j in range(13, 18):
				if not re.match(tic_fic_data['Commits Between'], row[j]):
					log.error(info_message(filename, i, header[j], row[j]))
			if not re.match(tic_fic_data['Days Between TIC-FIC'], row[18]):
				log.error(info_message(filename, i, header[18], row[18]))

def run_checks_pr(log):
	filename = 'pr-data.csv'
	with open(filename, newline = '') as csvfile:
		info = csv.reader(csvfile)
		header = next(info)
		validate_header(header, pr_data, filename, log)
		for i, row in enumerate(info):
			i += 2
			validate_common_rules(row, i, filename, header, log)
			# Avoid until pr-data.csv is fixed
			if row[3] == 'org.apache.dubbo.rpc.protocol.dubbo.MultiThreadTest.testDubboMultiThreadInvoke':
				continue
			if not all(x in pr_data['Category'] for x in row[4].split(';')):
				log.error(info_message(filename, i, header[4], row[4]))
			if not row[5] in pr_data['Status']: # Check the status is valid
			    log.error(info_message(filename, i, header[5], row[5]))
			if row[5] in ['Accepted', 'Opened', 'Rejected']:
				if not re.match(pr_data['PR Link'], row[6]):
					log.error(info_message(filename, i, header[6], row[6]))
			if not re.match(pr_data['Notes'], row[7]):
				log.error(info_message(filename, i, header[7], row[7]))

def main():
	# Taken from https://stackoverflow.com/a/45446664/9610524
	error_handler = errorhandler.ErrorHandler()
	stream_handler = logging.StreamHandler(stream=sys.stderr)
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)  
	logger.addHandler(stream_handler)

	checks = [run_checks_pr, run_checks_tic_fic, run_checks_tso_iso]
	for check in checks:
		check(logger)
	if error_handler.fired:
	    logger.critical('Failure: Exiting with code 1 due to logged errors.')
	    raise SystemExit(1)
main()



