#!/usr/bin/env python3.6

import os
import sys
import csv

# Import pandas
try:
	import pandas as pd
except:
	# If pandas is not installed, refer to installation page.
	print("This script requires the pandas package.\nYou can install pandas by following this guide:\nhttps://pandas.pydata.org/pandas-docs/stable/install.html#installing-pandas")
	# Exit code
	sys.exit(1)

# Import matplotlib
try:
	import matplotlib.pyplot as plt
except:

	# If matplotlib is not installed, refer to installation page.
	print("This script requires that the matplotlib package is installed. You can install matplotlib by following this guide:\nhttps://matplotlib.org/users/installing.html#installing\n")

	#Exit
	sys.exit(1)

# Initialize location and file names.
try:
	output_loc = sys.argv[1]

	if output_loc == "generic":
		loc_file = "./.docker_volume_generic.loc"
		results_name = "./results-generic.csv"
		total_con_name = "Total_Connections_results-generic.png"
		con_per_sec_name = "Connections_persec_results-generic.png"

	elif output_loc == "liboqs":
		loc_file = "./.docker_volume_liboqs.loc"
		results_name = "./results-liboqs.csv"
		total_con_name = "Total_Connections_results-liboqs.png"
		con_per_sec_name = "Connections_persec_results-liboqs.png"
	else:
		print("Incorrect directory specified.\nPlease choose one of the following:\n- generic\n- liboqs")
except:
	print("No file directory specified.\nPlease choose one of the following:\n- generic\n- liboqs")
	sys.exit(1)

def create_dataframe(data):
	"""
	This function is creating the a dataframe from the data provided by the worker_module() function.
	"""

	# Create list with columns to use in the dataframe.
	columns = ["Benchmark_number", "Cipher",
			"Connections_no_sidr", "Seconds_no_sidr", "Connections_user_second_no_sidr", "Real_seconds_no_sidr",
			"Connections_sidr", "Seconds_sidr", "Connections_user_second_sidr", "Real_seconds_no_sidr"]
	
	# Create dataframe from data and the columns specified above.
	df = pd.DataFrame(data, columns=columns)

	return df

def worker_module():
	"""
	This function parses the information from the data in the shared docker volume.
	"""	

	# Parse output location
	with open(loc_file) as vol_loc:
		data = vol_loc.read()
		vol_loc_clean = data.rstrip('\n')

	# Initialyse an emtpy list to store the results.
	final_results = []

	# Loop over the files in the specified directory
	for e, entry in enumerate(os.listdir(vol_loc_clean)):
		
		# Parse s-time results
		if entry.startswith("s-time"):
		
			# Strip prefix and suffix. Grab the benchmark_number
			entry_no_prefix = entry.strip("s-time_")
			entry_clean = entry_no_prefix.strip(".txt")
			benchmark_number = entry_clean[-1:]

			# Open each of the files
			with open(vol_loc_clean + '/' + entry, 'r') as f:
				data = f.readlines()
	
				# This splits every entry for the lines that make sense
				try:
					no_sidr = data[3].split(' ')
					no_sidr_real_sec = data[4].split(' ')
					sidr = data[11].split(' ')
					sidr_real_sec = data[12].split(' ')
				except:
					print("Invalid data in one of the output files, exiting parser.")
					sys.exit(1)

				# Initiate empy array in order to store the data
				result_array = []

				# [> General info <]

				result_array.append(benchmark_number)
				result_array.append(entry_clean)

				# [> No session id reuse data <]

				# No sidr connections
				result_array.append(no_sidr[0])

				# No sidr seconds
				no_sidr_sec = no_sidr[3]
				clean_no_sidr_sec = no_sidr_sec[:-2]
				result_array.append(clean_no_sidr_sec)

				# No sidr connections/user/sec
				result_array.append(no_sidr[4])

				# No sidr real seconds
				result_array.append(no_sidr_real_sec[3])

				# [> Session id reuse data <]
				
				# sidr connections
				result_array.append(sidr[0])
				
				# sidr seconds
				sidr_sec = sidr[3]
				clean_sidr_sec = sidr_sec[:-2]
				result_array.append(clean_sidr_sec)
				
				# sidr connections/user/sec
				result_array.append(sidr[4])
				
				# sidr real seconds			
				result_array.append(sidr_real_sec[3])

				# [> Finalyse <]

				# Append the parsed data to final result list
				final_results.append(result_array)
	
	# Return the list with final results.
	return final_results

def plot_results():
	"""
	This function takes the results.csv file and plots the data.
	"""

#	for file in os.listdir('./'):
#		if file.startswith('results') and file.endswith('.csv'):

	#read the csv file
	df = pd.read_csv(results_name)
	
	#Group by name and get the mean
	df = df.groupby("Cipher").mean().reset_index()

	#sorts the values of the file
	sort_by_connection = df.sort_values('Connections_sidr',ascending=False)
	sort_by_conpersec = df.sort_values("Connections_user_second_sidr")

	#fix size 
	fig = plt.figure(1)

	#Set a name for the supertittle
	fig.suptitle("Total Connections Per Cipher with Sidr")

	#set window size. Hardcoded
	fig.set_size_inches(18.5,10.5)

	#fig.set_size_inches(18.5,15.5)
	plt.bar(sort_by_connection.Cipher,sort_by_connection.Connections_sidr,align='edge',color="rgbky")

	#adjust the left margin so that all algorithms are visible
	plt.subplots_adjust(bottom=0.25)
	plt.ylim(75000,110000)
	plt.xticks(rotation=90, fontsize=6)

	#plt.yticks(fontsize=5)
	#I use figures to save and to put suptitle to the plot
	fig.savefig(total_con_name)

	fig = plt.figure(2)

	#Set a name for the supertittle
	fig.suptitle("Connections per cipher/user per Second with Sidr")

	#fig.set_size_inches(18.5,10.5)
	fig.set_size_inches(18.5,15.5)

	#plot a bargraph on y-axis
	plt.bar(sort_by_conpersec.Cipher,sort_by_conpersec.Connections_user_second_sidr,color="rgbky")

	#adjust the left margin so that all algorithms are visible
	plt.subplots_adjust(bottom=0.25)
	plt.ylim(8000,17000)

	#change the font size in x-axis
	plt.xticks(rotation=90, fontsize=6)
	plt.show()
		
	fig.savefig(con_per_sec_name)

	#print the results on terminal. 
#	print(df)

if __name__ == "__main__":
	"""
	Main function runs the worker module in order to parse the files in the shared volume, and the puts the data in a dataframe. Then it is parsed to csv.
	"""

	final_results = worker_module()
	df = create_dataframe(final_results)

	df.to_csv(results_name)	
#	print(df)

	
	plot_results()
