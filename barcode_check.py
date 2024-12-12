import csv
import subprocess #import subprocess to run external python scripts
def check_barcode_in_db(barcode): #open the csv file in read mode
	with open('barcode_db.csv', 'r') as file:
		csv_reader = csv.reader(file)
		next(csv_reader)
		for row in csv_reader:
			print(f"Row being processed: {row}")
			if len(row) != 2: #skip any row that has more than the expected 2 values
				print(f"Skipping invalid row: {row}")
				continue
			stored_barcode, result = row
			print(f"checking barcode: {stored_barcode}, Result: {result}")
			if stored_barcode is None or result is None:
				print(f"Error: Stored barcode is None for row: {row}")
				continue
			try:
				stored_barcode = int(stored_barcode)
			except ValueError:
				print(f"Warning: Stored barcode is not a number: {stored_barcode}")
				continue
			if barcode is None:
				print("Error: Scanned barcode is None.")
				return 'no'
			try:
				barcode = int(barcode)
			except ValueError:
				print(f"Warning: Scanned barcode is not a valid integer: {barcode}")
				return 'no'
			if barcode == stored_barcode:
				return result
	print("No barcode match found.")
	return 'no'
def trigger_servo_action(result):
	"""Trigger the appropriate script based on the result."""
	print(f"Triggering action for result: {result}")
	if result == 'yes':
		print('Result is "yes" - triggering recycle action...')
		subprocess.run(['python3', 'recycle.py'])
	elif result == 'no':
		print ('Result is "no" - Triggering landfill action...')
		subprocess.run(['python3', 'landfill.py'])
	else:
		print(f"Unexpected result: {result}")
scanned_barcode = input("Scan barcode:")
if not scanned_barcode:
	print("Error: No barcode scanned.")
else:
	result = check_barcode_in_db(scanned_barcode)
	print(f"Result: {result}")
	trigger_servo_action(result)
