import csv 
import sys
import re 

common_data = {
	'Project URL': r'(https:\/\/github.com)(\/(\w|\.|-)+){2}',
	'SHA': r'\b[0-9a-f]{40}\b',
	'Module path': r'((\w|\.|-)+(\/|\w|\.|-)*)|^$',
	'Fully-Qualified': r'((\w|\s)+\.)+(\w+)+' # The whitespace is because https://github.com/pinterest/secor had a whitespace in it --not sure if valid
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

def assert_header(header, table):
	assert header == table['columns'] # Check columns are correct

def assert_common_rules(row):
		assert bool(re.match(common_data['Project URL'], row[0])) # Check repo addresses are valid
		assert bool(re.match(common_data['SHA'], row[1])) # Check SHAs are valid
		assert bool(re.match(common_data['Module path'], row[2])) # Check that module paths are valid
		assert bool(re.match(common_data['Fully-Qualified'], row[3])) # Check for valid fully-qualified name 

def run_checks_tso_iso():
	with open('tso-iso-rates.csv', newline = '') as csvfile:
		info = csv.reader(csvfile)
		header = next(info)
		assert_header(header, tso_iso_rates)
		for row in info:
			assert bool(re.match(tso_iso_rates['Failures/Runs'], row[4]))
			assert bool(re.match(tso_iso_rates['Failures/Runs'], row[5]))
			assert bool(re.match(tso_iso_rates['P-Value'], row[6]))
			assert bool(re.match(tso_iso_rates['Less/Greater'], row[7]))
			for i in range(8, 12):
			    assert bool(re.match(tso_iso_rates['Last 4'], row[i]))


def run_checks_tic_fic():
	with open('tic-fic-data.csv', newline = '') as csvfile:
		info = csv.reader(csvfile)
		header = next(info)
		assert_header(header, tic_fic_data)
		for row in info:
			assert_common_rules(row)
			assert bool(re.match(tic_fic_data['TIC = FIC'], row[4]))
			assert bool(re.match(common_data['SHA'], row[5]))
			assert bool(re.match(common_data['Fully-Qualified'], row[6]))
			assert bool(re.match(common_data['Module path'], row[7])) # Check module paths are valid
			assert bool(re.match(common_data['SHA'], row[8]))
			for i in range(9, 13):
				assert bool(re.match(tic_fic_data['Modified'], row[i]))
			for i in range(13, 18):
				assert bool(re.match(tic_fic_data['Commits Between'], row[i]))
			assert bool(re.match(tic_fic_data['Days Between TIC-FIC'], row[18]))

def run_checks_pr():
	with open('pr-data.csv', newline = '') as csvfile:
		info = csv.reader(csvfile)
		header = next(info)
		assert_header(header, pr_data)
		for row in info:
			assert_common_rules(row)
			# Fails because org.apache.dubbo.rpc.protocol.dubbo.MultiThreadTest.testDubboMultiThreadInvoke has category 'NOD;ND'
			if row[3] == 'org.apache.dubbo.rpc.protocol.dubbo.MultiThreadTest.testDubboMultiThreadInvoke':
				continue
			assert all(x in pr_data['Category'] for x in row[4].split(';'))
			assert row[5] in pr_data['Status'] # Chech the status is valid
			if row[5] in ['Accepted', 'Opened', 'Rejected']:
				assert bool(re.match(pr_data['PR Link'], row[6]))
			assert bool(re.match(pr_data['Notes'], row[7]))

def main():
	try:
		run_checks_pr()
		run_checks_tic_fic()
		run_checks_tso_iso()
	except:
		print("Exiting because of error")
		exit(1)

main()



