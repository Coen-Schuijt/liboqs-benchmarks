#!/usr/bin/env python3

import time
import os

def initialyse():
	"""
	Function that stops any running docker containers, rebuilds the image from the docker file, creates a local volume and runs the benchmark-container in detached mode. Sets sysctl settings in order to run the benchmarks.
	"""

	# Start docker deamon.
	print("[ Starting docker deamon ]")
	os.system("/bin/systemctl start docker.service")

	# Stop running container.
	print("\n[ Stopping running container ]")
	os.system("docker stop benchmark-container")

	# Build the benchmark-container from the Dockerfile.
	print("\n[ Building docker container ]")
	os.system("docker build . -t benchmark-container")

	# Create a volume to store results locally.
	print("\n[ Creating docker volume ]")
	os.system("docker volume create benchmark-results-generic")
	os.system("docker volume inspect --format '{{ .Mountpoint }}' benchmark-results-generic > ./.docker_volume_generic.loc")

	# Start the docker container (detached).
	print("\n[ Running docker container ]")
	os.system("docker run --rm -i -t -d --name benchmark-container -v benchmark-results-generic:/usr/local/liboqs-benchmarks/results benchmark-container /bin/bash")

	# The following configurations are used in order to run the s_time benchmarks.
	print("\n[ Changing system settings ]")
	os.system("sysctl net.ipv4.tcp_tw_recycle='1'")
	os.system("sysctl net.ipv4.tcp_tw_reuse='1'")

	# Create directory and copy the openssl.cnf file. This makes sure the warning is supressed.
	os.system("docker exec -i -t benchmark-container bash -c 'mkdir -p /usr/local/ssl/ ; cp /etc/ssl/openssl.cnf /usr/local/ssl/openssl.cnf'")
	
	return

def generate_ssc():
	"""
	This function creates a self signed certificate and creates a pem file which is used for the s_server function.
	"""

	# Create Self Signed Certificate (RSA).
	print("\n[ Creating Self Signed Certificate (RSA) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl/apps/openssl req -x509 -new -newkey rsa:2048 -nodes -sha256 -days 365 -config openssl/apps/openssl.cnf -subj \"/C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl\" -keyout server-rsa.key -out server-rsa.cert'")

	# Create pem file in order to use it with SSL/TLS server.
	print("\n[ Concatenating key and cert ]")
	os.system("docker exec -i -t benchmark-container bash -c 'cat server-rsa.key server-rsa.cert > server-rsa-cert.pem'")
	
	# Create Self Signed Certificate for ECDSA.
	print("\n[ Creating Self Signed Certificate (ECDSA) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl req -new -days 365 -nodes -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -subj \"/C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl\" -keyout server-ecdsa.key -out server-ecdsa.cert'")

	return

def run_server():
	"""
	This function opens several SSL/TLS servers on port 4444-4448 in order to accept various ciphers.
	"""

	# Setup SSL/TLS server for [4444] ECDSA.
	print("\n[ Setting up SSL/TLS Server (ECDSA) ... Listening on port 4444 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4444 -cert server-ecdsa.cert -key server-ecdsa.key'")

	# Setup SSL/TLS server for [4445] RSA.
	print("\n[ Setting up SSL/TLS Server (RSA) ... Listening on port 4445 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4445 -cert server-rsa-cert.pem'")

	return

def generate_file_loc(file_name):
	"""
	This function reads the file path for the docker-volume and then returns the file path + file name.
	"""

	# File handler. This generates the full file path and file name.
	with open('./.docker_volume_generic.loc') as vol_loc:
		data = vol_loc.read()
		data_clean = data.rstrip('\n')	
		file_loc = data_clean + "/" + file_name
	
	return file_loc

def generate_ciphers_liboqs():
	"""
	This function creates an array of ciphers to be used by the client.
	"""

	# This generates a list with the ciphers and outputs it to the shared storage.
	os.system("docker exec -i -t benchmark-container bash -c 'openssl/apps/openssl ciphers OQSKEM-DEFAULT:OQSKEM-DEFAULT-ECDHE > ./results/ciphers_liboqs.txt 2>&1'")
	
	# File handler (liboqs ciphers). This generates the full file path.
	file_loc = generate_file_loc("ciphers_liboqs.txt")

	# This reads the ciphers from the file.
	with open(file_loc) as file:
		data = file.read()
	
		# Strip trailing newline.
		data_no_trail = data.rstrip('\n')

		# Split for later use.
		data_array_liboqs = data_no_trail.split(':')

		# Return the definitive list.
		return data_array_liboqs
		
def generate_ciphers_generic():
	"""
	This function creates an array of ciphers to be used by the client.
	"""

	# This generates a list with the ciphers and outputs it to the shared storage.
	os.system("docker exec -i -t benchmark-container bash -c 'openssl/apps/openssl ciphers > ./results/ciphers_generic.txt 2>&1'")

	# File handler (generic ciphers). This generates the full file path.
	file_loc = generate_file_loc("ciphers_generic.txt")

	# This reads the ciphers from the file.
	with open(file_loc) as file:
                data = file.read()
        
                # Strip trailing newline.
                data_no_trail = data.rstrip('\n')

                # Split for later use.
                data_array_generic = data_no_trail.split(':')

                # Return the definitive list.
                return data_array_generic

def run_client():
	"""
	This function runs each of the ciphers as part of the array containing difference of the generate_ciphers_liboqs() and generate_ciphers_generic() functions, against the server. Sleeps 10 seconds after every cipher.
	"""

	# Generate a list of ciphers.
	cipherlist_liboqs = generate_ciphers_liboqs() 
	cipherlist_generic = generate_ciphers_generic()
	
	# Remove entries from generic list that are in liboqs list.
	cipherlist = [i for i in cipherlist_generic if not i in cipherlist_liboqs or cipherlist_generic.remove(i)]

	# Cast the cipherlist to a string in order to write to disk.
	cipher_string = ""
	for item in cipherlist:
		cipher_string += "{}:".format(item)
	
	# Remove trailing colon.
	cipher_generic = cipher_string.rstrip(':')

	# File handler (generic ciphers). This generates the full file path.
	file_loc = generate_file_loc("ciphers_generic.txt")

	# Write final cipherlist (generic ciphers without OQSKEM ciphers) to ciphers_generic file.
	with open(file_loc, 'w') as file:
		file.write(cipher_generic)

	# Generate seperate lists for non-/ecdsa ciphers.
	generic_ecdsa_cipherlist = []
	generic_rsa_cipherlist = []

	# Checks all items in the cipherlist and appends items to corresponding list.
	for item in cipherlist:

		# [4444] ECDSA.
		if "ECDSA" in item:
			generic_ecdsa_cipherlist.append(item)

		# [4449] All Others.
		else:
			generic_rsa_cipherlist.append(item)

	print("\n[ Creating generic ECDSA cipherlist ]\n{}".format(generic_ecdsa_cipherlist))
	print("\n[ Creating generic RSA cipherlist ]\n{}".format(generic_rsa_cipherlist))

	# Default = 30
	duration = 30

	# Run benchmarks for generic [4444] ECDSA ciphers.
	print("\n[> Running tests for generic_ecdsa_ciphers <]")
	for item in generic_ecdsa_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4444 -cipher {0} -cert server-ecdsa.cert -key server-ecdsa.key -time {1} > ./results/s-time_ecdsa_{0}_`ls ./results/s-time_ecdsa_{0}_* | wc -l`.txt 2>&1'".format(item, duration)
		
		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)
	
		print("[ Sleeping for 70 seconds ]") 
		time.sleep(70)

	# Run benchmarks for generic [4445] RSA ciphers.
	print("\n[> Running tests for generic_rsa_ciphers <]")
	for item in generic_rsa_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4445 -cipher {0} -cert server-rsa-cert.pem -time {1} > ./results/s-time_rsa_{0}_`ls ./results/s-time_rsa_{0}_* | wc -l`.txt 2>&1'".format(item, duration)
	
		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)
	
		print("[ Sleeping for 70 seconds ]") 
		time.sleep(70)

	return

if __name__ == "__main__":
	"""
	Main function initialyses the Docker environment, generates a self signed certificate, then starts a SSL/TLS server and finally runs benchmarks for al of these algorithms.
	"""	

	# Run functions	
	initialyse()
	generate_ssc()
	run_server()
	run_client()

#	os.system("sudo parse_client_server.py")
