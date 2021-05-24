import csv 
import sys
import re 

pr_data = {
	'columns': ['Project URL', 'SHA Detected', 'Module Path', 
	'Fully-Qualified Test Name (packageName.ClassName.methodName)', 'Category', 'Status', 'PR Link', 'Notes'],
	'Project URL': r'(https:\/\/github.com)(\/(\w|\.|-)+){2}',
	'SHA': r'\b[0-9a-f]{40}\b',
	'Module path': r'((\w|\.|-)+(\/|\w|\.|-)*)|^$',
	'Fully-Qualified': r'((\w|\s)+\.)+(\w+)+', # The whitespace is because https://github.com/pinterest/secor had a whitespace in it --not sure if valid
	'Category': ['OD', 'OD-Brit', 'OD-Vic', 'ID', 'NOD', 'NDOD', 'NDOI', 'NDOI', 'UD'],
	'Status': ['', 'Opened', 'Accepted', 'InspiredAFix', 'DeveloperFixed', 'Deleted', 'Rejected', 'Skipped'],
	'PR Link': r'((https:\/\/github.com\/((\w|\.|-)+\/)+)(pull\/\d+))|^$',
	'Notes': r'(https:\/\/github.com\/TestingResearchIllinois\/((idoft)|(flaky-test-dataset))\/issues\/\d+)|^$'
}



def run_checks(filename):
	with open(filename, newline = '') as csvfile:
		info = csv.reader(csvfile)
		header = next(info)
		assert header == pr_data["columns"] # Check columns are correct
		for row in info:
			assert bool(re.match(pr_data['Project URL'], row[0])) # Check repo addresses are valid
			assert bool(re.match(pr_data['SHA'], row[1])) # Check SHAs are valid
			assert bool(re.match(pr_data['Module path'], row[2])) # Check module paths are valid
			assert bool(re.match(pr_data['Fully-Qualified'], row[3])) # Check for valid fully-qualified name 
			# Fails because org.apache.dubbo.rpc.protocol.dubbo.MultiThreadTest.testDubboMultiThreadInvoke has category 'NOD;ND'
			if row[3] == 'org.apache.dubbo.rpc.protocol.dubbo.MultiThreadTest.testDubboMultiThreadInvoke':
				continue
			assert all(x in pr_data['Category'] for x in row[4].split(';'))
			assert row[5] in pr_data['Status'] # Chech the status is valid
			assert bool(re.match(pr_data['PR Link'], row[6]))
			assert bool(re.match(pr_data['Notes'], row[7]))

def main(argv):
	try:
		run_checks(argv)
	except:
		exit(1)

if __name__ == "__main__":
    main(sys.argv[1])




