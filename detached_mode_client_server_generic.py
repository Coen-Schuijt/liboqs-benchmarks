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

	# Create Self Signed Certificate for DH-DSS.
	print("\n[ Creating Self Signed Certificate (DH-DSS) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl dhparam -out server-dh-dss-param.pem 2048 && openssl genpkey -paramfile server-dh-dss-param.pem -out server-dh-dss-key.pem && openssl pkey -in server-dh-dss-key.pem -pubout -out server-dh-dss-pubkey.pem && openssl dsaparam -out server-dss-param.pem 2048 && openssl gendsa -out server-dss-key.pem server-dss-param.pem && openssl req -new -key server-dss-key.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-dss-req.pem && openssl x509 -req -in server-dss-req.pem -signkey server-dss-key.pem -out server-dss-cert.cert && openssl req -new -key server-dss-key.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-dh-dss.csr && openssl x509 -req -in server-dh-dss.csr -CAkey server-dss-key.pem -CA server-dss-cert.cert -force_pubkey server-dh-dss-pubkey.pem -out server-dh-dss-cert.cert -CAcreateserial'")
	
	# Create Self Signed Certificate for DH-RSA.
	print("\n[ Creating Self Signed Certificate (DH-RSA) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl dhparam -out server-dh-rsa-param.pem 2048 && openssl genpkey -paramfile server-dh-rsa-param.pem -out server-dh-rsa-key.pem && openssl pkey -in server-dh-rsa-key.pem -pubout -out server-dh-rsa-pubkey.pem && openssl genrsa -out server-dh-rsa-key.pem 2048 && openssl req -new -key server-dh-rsakey.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-dh-rsa.csr && openssl x509 -req -in server-dh-rsa.csr -CAkey server-rsa.key -CA server-rsa.cert -force_pubkey server-dh-rsa-pubkey.pem -out server-dh-cert.cert -CAcreateserial'")

	# Create self signed certificate for ECDH-RSA.	
	print("\n[ Creating Self Signed Certificate (ECDH-RSA) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl/apps/openssl ecparam -out server-ecdh-param.pem -name prime256v1 && openssl genpkey -paramfile server-ecdh-param.pem -out server-ecdh-key.pem && openssl pkey -in server-ecdh-key.pem -pubout -out server-ecdh-pubkey.pem && openssl genrsa -out server-ecdh-rsakey.pem 2048 && openssl req -new -key server-ecdh-rsakey.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-ecdh-rsa.csr && openssl x509 -req -in server-ecdh-rsa.csr -CAkey server-rsa.key -CA server-rsa.cert -force_pubkey server-ecdh-pubkey.pem -out server-ecdh-cert.cert -CAcreateserial'") 

	return

def run_server():
	"""
	This function opens several SSL/TLS servers on port 4444-4448 in order to accept various ciphers.
	"""

	# Setup SSL/TLS server for [4444] ECDSA.
	print("\n[ Setting up SSL/TLS Server (ECDSA) ... Listening on port 4444 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4444 -cert server-ecdsa.cert -key server-ecdsa.key'")

	# Setup SSL/TLS server for [4445] DH-DSS.
	print("\n[ Setting up SSL/TLS Server (DH-DSS) ... Listening on port 4445 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4445 -cert server-dh-dss-cert.cert -key server-dh-dss-key.pem'")

	# Setup SSL/TLS server for [4446] DHE-DSS/EDH-DSS.
	print("\n[ Setting up SSL/TLS Server (DHE-DSS) ... Listening on port 4446 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4446 -cert server-dss-cert.cert -key server-dss-key.pem'")

	# Setup SSL/TLS server for [4447] DH-RSA.
	print("\n[ Setting up SSL/TLS Server (DH-RSA) ... Listening on port 4447 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4447 -cert server-dh-rsa-cert.cert -key server-dh-rsa-key.pem'")

	# Setup SSL/TLS server for [4448] ECDH-RSA.
	print("\n[ Setting up SSL/TLS Server (ECDH-RSA) ... Listening on port 4448 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4448 -cert server-ecdh-cert.cert -key server-ecdh-key.pem'")

	# Setup SSL/TLS server for [4449] RSA.
	print("\n[ Setting up SSL/TLS Server (RSA) ... Listening on port 4449 ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_server -accept 4449 -cert server-rsa-cert.pem'")

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
	generic_dh_dss_cipherlist = []
	generic_dhe_dss_cipherlist = []
	generic_dh_rsa_cipherlist = []
	generic_ecdh_rsa_cipherlist = []
	generic_srp_cipherlist = []
	generic_psk_cipherlist = []
	generic_gost_cipherlist = []
	generic_rsa_cipherlist = []

	# Checks all items in the cipherlist and appends items to corresponding list.
	for item in cipherlist:

		# [4444] DSA.
		if "ECDSA" in item:
			generic_ecdsa_cipherlist.append(item)

		# [4445] DH-DSS.
		elif item.startswith("DH-DSS"):
			generic_dh_dss_cipherlist.append(item)
		
		# [4446] DHE-DSS/EDH-DSS.
		elif item.startswith("DHE-DSS") or item.startswith("EDH-DSS"):
			generic_dhe_dss_cipherlist.append(item)

		# [4447] DH-RSA.
		elif item.startswith("DH-RSA"):
			generic_dh_rsa_cipherlist.append(item)

		# [4448] ECDH-RSA.
		elif item.startswith("ECDH-RSA"):
			generic_ecdh_rsa_cipherlist.append(item)

		# [----] SRP.
		elif item.startswith("SRP"):
			generic_srp_cipherlist.append(item)

		# [----] PSK.
		elif item.startswith("PSK"):
			generic_psk_cipherlist.append(item)
		
		# [----] GOST.
		elif item.startswith("GOST"):
			generic_gost_cipherlist.append(item)
	
		# [4449] All Others.
		else:
			generic_rsa_cipherlist.append(item)

	print("\n[ Creating generic ECDSA cipherlist ]\n{}".format(generic_ecdsa_cipherlist))
	print("\n[ Creating generic DH-DSS cipherlist ]\n{}".format(generic_dh_dss_cipherlist))
	print("\n[ Creating generic DHE-DSS cipherlist ]\n{}".format(generic_dhe_dss_cipherlist))
	print("\n[ Creating generic DH-RSA cipherlist ]\n{}".format(generic_dh_rsa_cipherlist))
	print("\n[ Creating generic ECDH-RSA cipherlist ]\n{}".format(generic_ecdh_rsa_cipherlist))	
	print("\n[ Creating generic RSA cipherlist ]\n{}".format(generic_rsa_cipherlist))

	# Debug mode

	# Default = 30
	duration = 1

	# Default = 70
	sleep = 2

	# Run benchmarks for generic [4444] ECDSA ciphers.
	print("\n[> Running tests for generic_ecdsa_ciphers <]")
	for item in generic_ecdsa_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4444 -cipher {0} -cert server-ecdsa.cert -key server-ecdsa.key -time {1} > ./results/s-time_{0}_`ls ./results/s-time_{0}_* | wc -l`.txt 2>&1'".format(item, duration)
		
		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)
	
		print("[ Sleeping for 70 seconds ]") 
		time.sleep(sleep)

	# Run benchmarks for generic [4445] DH-DSS ciphers.
	print("\n[> Running tests for generic_dh_dss_ciphers <]")
	for item in generic_dh_dss_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4445 -cipher {0} -cert server-dh-dss-cert.cert -key server-dh-dss-key.pem -time {1} > ./results/s-time_{0}_`ls ./results/s-time_{0}_* | wc -l`.txt 2>&1'".format(item, duration)

		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)

		print("[ Sleeping for 70 seconds ]")
		time.sleep(70)

	# Run benchmarks for generic [4446] DHE-DSS/EDH-DSS ciphers.
	print("\n[> Running tests for generic_dhe_dss_ciphers <]")
	for item in generic_dhe_dss_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4446 -cipher {0} -cert server-dss-cert.cert -key server-dss-key.pem -time {1} > ./results/s-time_{0}_`ls ./results/s-time_{0}_* | wc -l`.txt 2>&1'".format(item, duration)
		
		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)

		print("[ Sleeping for 70 seconds]") 
		time.sleep(70)

	# Run benchmarks for generic [4447] DH-RSA ciphers.
	print("\n[> Running tests for generic_dh_rsa_ciphers <]")
	for item in generic_dh_rsa_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4447 -cipher {0} -cert server-dh-rsa-cert.cert -key server-dh-rsa-key.pem -time {1} > ./results/s-time_{0}_`ls ./results/s-time_{0}_* | wc -l`.txt 2>&1'".format(item, duration)

		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)
	
		print("[ Sleeping for 70 seconds ]")
		time.sleep(70)

	# Run benchmark for generic [4448] ECDH-RSA ciphers.
	print("\n[> Running tests for generic_ecdh_rsa_ciphers <]")
	for item in generic_ecdh_rsa_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4448 -cipher {0} -cert server-ecdh-cert.cert -key server-ecdh-key.pem -time {1} > ./results/s-time_{0}_`ls ./results/s-time_{0}_* | wc -l`.txt 2>&1'".format(item, duration)

		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)
	
		print("[ Sleeping for 70 seconds ]")
		time.sleep(70)

	# Run benchmarks for generic [4449] RSA ciphers.
	print("\n[> Running tests for generic_rsa_ciphers <]")
	for item in generic_rsa_cipherlist:
		command = "docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl s_time -connect localhost:4449 -cipher {0} -cert server-rsa-cert.pem -time {1} > ./results/s-time_{0}_`ls ./results/s-time_{0}_* | wc -l`.txt 2>&1'".format(item, duration)
	
		print("\n[ Running benchmarks for [{}] for 60 seconds ]".format(item))
#		print(command)
		os.system(command)
	
		print("[ Sleeping for 70 seconds ]") 
		time.sleep(sleep)

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
