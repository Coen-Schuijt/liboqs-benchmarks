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
		path = "./generic_png/"
		if not os.path.exists(path):
			os.makedirs(path)
		loc_file = "./.docker_volume_generic.loc"
		results_name = "./results-generic.csv"
		total_con_name = "Total_Connections_results_generic_sidr.png"
		con_per_sec_name = "Connections_persec_results_generic_sidr.png"
		total_con_name_no_sidr = "Total_Connections_results_generic_no_sird.png"
		con_per_sec_name_no_sidr = "Connections_persec_results_generic_no_sird.png"
		signature_algorithms_list=["rsa","ECDSA"]


	elif output_loc == "liboqs":
		path = "./liboqs_png/"
		if not os.path.exists(path):
			os.makedirs(path)
		loc_file = "./.docker_volume_liboqs.loc"
		results_name = "./results-liboqs.csv"
		total_con_name = "Total_Connections_results_liboqs_sidr.png"
		con_per_sec_name = "Connections_persec_results_liboqs_sidr.png"
		total_con_name_no_sidr = "Total_Connections_results_liboqs_no_sird.png"
		con_per_sec_name_no_sidr = "Connections_persec_results_liboqs_no_sird.png"
		signature_algorithms_list=["rsa","qteslaI_","qteslaIIIsize","qteslaIIIspeed","picnic"]

	else:
		sys.exit(1)

except:
	print("Incorrect directory specified.\nusage: ./parse_client_server.py [liboqs | generic]")
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
			entry_no_prefix = entry[7:] 
			entry_no_suffix = entry_no_prefix.strip(".txt")
			entry_clean = entry_no_suffix[:-2]
			benchmark_number = entry_no_suffix[-1:]

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

	plt.style.use('seaborn-darkgrid')
#	print(plt.style.available)

	# Read the csv file
	df = pd.read_csv(results_name)
	
	# Group by name and get the mean
	df = df.groupby("Cipher").mean().reset_index()


	# Sort the values of the file
	sort_by_connection_no_sidr = df.sort_values('Connections_no_sidr',ascending=False)
	sort_by_conpersec_no_sidr = df.sort_values("Connections_user_second_no_sidr", ascending=False)

	sort_by_connection_sidr = df.sort_values('Connections_sidr',ascending=False)
	sort_by_conpersec_sidr = df.sort_values("Connections_user_second_sidr", ascending=False)


	#FIGURE 1 TOTAL CONNECTIONS PER CIPHER WITH SIDR

	# Fix size 
	fig = plt.figure(1)
	# Set a name for the supertittle
	fig.suptitle("Total Connections Per Cipher with Sidr")
	# Set window size. Hardcoded
	fig.set_size_inches(18.5,10.5)
	plt.bar(sort_by_connection_sidr.Cipher,sort_by_connection_sidr.Connections_sidr)
	#Set label for the y-axis
	plt.ylabel('No of Total Connections')
	#adjust the left margin so that all algorithms are visible
	plt.subplots_adjust(bottom=0.25)
	plt.xticks(rotation=90, fontsize=15)
	#Set label for the x-axis
	plt.xlabel("Algorithm Name")
	#I use figures to save and to put suptitle to the plot
	fig.savefig(path+total_con_name)	
#	os.system("eog {}".format(total_con_name))


	#FIGURE 2 CONNECTIONS PER CIPHER/USER_SECONDS WITH SIDR

	fig = plt.figure(2)
	#Set a name for the supertittle
	fig.suptitle("Connections of each Cipher per user seconds with Sidr")
	#fig.set_size_inches(18.5,10.5)
	fig.set_size_inches(18.5,10.5)
	#plot a bargraph on y-axis
	plt.bar(sort_by_conpersec_sidr.Cipher,sort_by_conpersec_sidr.Connections_user_second_sidr)
	#adjust the left margin so that all algorithms are visible
	plt.subplots_adjust(bottom=0.25)
	#Set label for the y-axis
	plt.ylabel('No of Connections')
	#change the font size in x-axis
	plt.xticks(rotation=90, fontsize=15)
	#Set label for the x-axis
	plt.xlabel("Algorithm Name")
	fig.savefig(path+con_per_sec_name)
#	os.system("eog {}".format(con_per_sec_name))


	#FIGURE 3-7 CONNECTIONS PER CIPHER/USER SECOND WITH SIDR

	for e,item in enumerate(signature_algorithms_list):
		signature_algo = df[df["Cipher"].str.contains(item)]
		fig = plt.figure(e+3)
		#Set a name for the supertittle
		fig.suptitle("Connections per 30 seconds in user mode")
		#fig.set_size_inches(18.5,10.5)
		fig.set_size_inches(18.5,10.5)
		#plot a bargraph on y-axis
		plt.bar(signature_algo.Cipher,signature_algo.Connections_user_second_sidr)
		#adjust the left margin so that all algorithms are visible
		plt.subplots_adjust(bottom=0.25)
		#Set label for the y-axis
		plt.ylabel('No of Connections')
		#change the font size in x-axis
		plt.xticks(rotation=90, fontsize=15)
		#Set label for the x-axis
		plt.xlabel("Algorithm Name")
		fig.savefig("{2}{1}_{0}".format(con_per_sec_name,item,path))
#		os.system("eog {1}_{0}".format(con_per_sec_name,item))	

	#FIGURE 8 CONNECTIONS PER CIPHER/USER_SECOND WITH SIDR- WITH DIFFERENT COLORS FOR EACH SIGNATURE ALGORITHM
	for e,item in enumerate(signature_algorithms_list):
		signature_algo = df[df["Cipher"].str.contains(item)]
		fig = plt.figure(8)
		#Set a name for the supertittle
		fig.suptitle("Connections per cipher/user per Second with Sidr")
		#fig.set_size_inches(18.5,10.5)
		fig.set_size_inches(18.5,10.5)
		#plot a bargraph on y-axis
		plt.bar(signature_algo.Cipher,signature_algo.Connections_user_second_sidr)
		#adjust the left margin so that all algorithms are visible
		plt.subplots_adjust(bottom=0.25)
		#Set label for the y-axis
		plt.ylabel('No of Connections')
		#change the font size in x-axis
		plt.xticks(rotation=90, fontsize=15)
		#Set label for the x-axis
		plt.xlabel("Algorithm Name")
		if item==signature_algorithms_list[-1]:
			fig.savefig("{}all_signatures_sidr.png".format(path))
#			os.system("eog all_signatures_sidr.png")

#--------------------------NO SIDR ------------------------------------------#

	#FIGURE 9 TOTAL CONNECTIONS PER CIPHER WITH NO SIDR

	# Fix size 
	fig = plt.figure(9)
	# Set a name for the supertittle
	fig.suptitle("Total Connections Per Cipher without Sidr")
	# Set window size. Hardcoded
	fig.set_size_inches(18.5,10.5)
	plt.bar(sort_by_connection_no_sidr.Cipher,sort_by_connection_no_sidr.Connections_no_sidr)
	#Set label for the y-axis
	plt.ylabel('No of Total Connections')
	#adjust the left margin so that all algorithms are visible
	plt.subplots_adjust(bottom=0.25)
	plt.xticks(rotation=90, fontsize=15)
	#Set label for the x-axis
	plt.xlabel("Algorithm Name")
	#I use figures to save and to put suptitle to the plot
	fig.savefig(path+total_con_name_no_sidr)	
#	os.system("eog {}".format(total_con_name))


	#FIGURE 10 CONNECTIONS PER CIPHER/USER_SECONDS WITH NO SIDR

	fig = plt.figure(10)
	#Set a name for the supertittle
	fig.suptitle("Connections of each Cipher per user seconds without Sidr")
	#fig.set_size_inches(18.5,10.5)
	fig.set_size_inches(18.5,10.5)
	#plot a bargraph on y-axis
	plt.bar(sort_by_conpersec_no_sidr.Cipher,sort_by_conpersec_no_sidr.Connections_user_second_no_sidr)
	#adjust the left margin so that all algorithms are visible
	plt.subplots_adjust(bottom=0.25)
	#Set label for the y-axis
	plt.ylabel('No of Connections')
	#change the font size in x-axis
	plt.xticks(rotation=90, fontsize=15)
	#Set label for the x-axis
	plt.xlabel("Algorithm Name")
	fig.savefig(path+con_per_sec_name_no_sidr)
#	os.system("eog {}".format(con_per_sec_name))


	#FIGURE 11-15 CONNECTIONS PER CIPHER/USER SECOND WITH NO SIDR

	for e,item in enumerate(signature_algorithms_list):
		signature_algo = df[df["Cipher"].str.contains(item)]
		fig = plt.figure(e+11)
		#Set a name for the supertittle
		fig.suptitle("Connections per 30 seconds in user mode without Sidr")
		#fig.set_size_inches(18.5,10.5)
		fig.set_size_inches(18.5,10.5)
		#plot a bargraph on y-axis
		plt.bar(signature_algo.Cipher,signature_algo.Connections_user_second_no_sidr)
		#adjust the left margin so that all algorithms are visible
		plt.subplots_adjust(bottom=0.25)
		#Set label for the y-axis
		plt.ylabel('No of Connections')
		#change the font size in x-axis
		plt.xticks(rotation=90, fontsize=15)
		#Set label for the x-axis
		plt.xlabel("Algorithm Name")
		fig.savefig("{2}{1}_{0}".format(con_per_sec_name_no_sidr,item,path))
#		os.system("eog {1}_no_sidr_{0}".format(con_per_sec_name_no_sidr,item))	

	#FIGURE 16 CONNECTIONS PER CIPHER/USER_SECOND WITH NO SIDR- WITH DIFFERENT COLORS FOR EACH SIGNATURE ALGORITHM
	for e,item in enumerate(signature_algorithms_list):
		signature_algo = df[df["Cipher"].str.contains(item)]
		fig = plt.figure(16)
		#Set a name for the supertittle
		fig.suptitle("Connections of each Cipher per user seconds without Sidr")
		#fig.set_size_inches(18.5,10.5)
		fig.set_size_inches(18.5,10.5)
		#plot a bargraph on y-axis
		plt.bar(signature_algo.Cipher,signature_algo.Connections_user_second_no_sidr)
		#adjust the left margin so that all algorithms are visible
		plt.subplots_adjust(bottom=0.25)
		#Set label for the y-axis
		plt.ylabel('No of Connections')
		#change the font size in x-axis
		plt.xticks(rotation=90, fontsize=15)
		#Set label for the x-axis
		plt.xlabel("Algorithm Name")
		if item==signature_algorithms_list[-1]:
			fig.savefig("{}all_signatures_without_sidr.png".format(path))
#			os.system("eog all_signatures_without_sidr.png")






if __name__ == "__main__":
	"""
	Main function runs the worker module in order to parse the files in the shared volume, and the puts the data in a dataframe. Then it is parsed to csv.
	"""

	final_results = worker_module()
	df = create_dataframe(final_results)

	df.to_csv(results_name)	
#	print(df)

	
	plot_results()
