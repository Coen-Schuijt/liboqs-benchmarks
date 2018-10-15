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
	os.system("docker volume create benchmark-results")
	os.system("docker volume inspect --format '{{ .Mountpoint }}' benchmark-results > ./.docker_volume.loc") 

	# Start the docker container (detached).
	print("\n[ Running docker container ]")
	os.system("docker run --rm -i -t -d --name benchmark-container -v benchmark-results:/usr/local/liboqs-benchmarks/results benchmark-container /bin/bash")

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

	# Create Self Signed Certificate (DH-DSS).
	print("\n[ Creating Self Signed Certificate (DH/DSS) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl dhparam -out server-dh-dss-param.pem 2048 && openssl genpkey -paramfile server-dh-dss-param.pem -out server-dh-dss-key.pem && openssl pkey -in server-dh-dss-key.pem -pubout -out server-dh-dss-pubkey.pem && openssl dsaparam -out server-dss-param.pem 2048 && openssl gendsa -out server-dss-key.pem server-dss-param.pem && openssl req -new -key server-dss-key.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-dss-req.pem && openssl x509 -req -in server-dss-req.pem -signkey server-dss-key.pem -out server-dss-cert.cert && openssl req -new -key server-dss-key.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-dh-dss.csr && openssl x509 -req -in server-dh-dss.csr -CAkey server-dss-key.pem -CA server-dss-cert.cert -force_pubkey server-dh-dss-pubkey.pem -out server-dh-dss-cert.cert -CAcreateserial'")

	# Create Self Signed Certificate for DH-RSA.
	print("\n[ Creating Self Signed Certificate (DH-RSA) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl genpkey -paramfile server-dh-param.pem -out server-dh-key.pem && openssl pkey -in server-dh-key.pem -pubout -out server-dh-pubkey.pem && openssl genrsa -out server-dh-rsakey.pem 2048 && openssl req -new -key server-dh-rsakey.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-dh-rsa.csr && openssl x509 -req -in server-dh-rsa.csr -CAkey server-rsa.key -CA server-rsa.cert -force_pubkey server-dh-pubkey.pem -out server-dh-cert.cert -CAcreateserial'")

	# Create self signed certificate for ECDH-RSA.  
	print("\n[ Creating Self Signed Certificate (ECDH-RSA) ]")
	os.system("docker exec -i -t benchmark-container bash -c 'openssl/apps/openssl ecparam -out server-ecdh-param.pem -name prime256v1 && openssl genpkey -paramfile server-ecdh-param.pem -out server-ecdh-key.pem && openssl pkey -in server-ecdh-key.pem -pubout -out server-ecdh-pubkey.pem && openssl genrsa -out server-ecdh-rsakey.pem 2048 && openssl req -new -key server-ecdh-rsakey.pem -subj /C=NL/ST=Amsterdam/L=Amsterdam/O=OS3/OU=RESEARCH/CN=os3.nl -out server-ecdh-rsa.csr && openssl x509 -req -in server-ecdh-rsa.csr -CAkey server-rsa.key -CA server-rsa.cert -force_pubkey server-ecdh-pubkey.pem -out server-ecdh-cert.cert -CAcreateserial'")

	return

def generate_file_loc(filename):
	"""
	This function reads the file path for the docker-volume and then returns the filepath + file name.
	"""
	
	# File handler. This generates the full file path and file name.
	with open('./.docker_volume.loc') as vol_loc:
		data = vol_loc.read()
		data_clean = data.rstrip('\n')
		file_loc = data_clean + "/" + filename

	return file_loc

def generate_ciphers_liboqs():
	"""
	This function creates an array of ciphers to be used by the client.
	"""

	# This generates a list with the ciphers and outputs it to the shared storage.
	os.system("docker exec -i -t benchmark-container bash -c 'openssl/apps/openssl ciphers OQSKEM-DEFAULT:OQSKEM-DEFAULT-ECDHE > ./results/ciphers_liboqs.txt 2>&1'")

	# File handler.
	file_loc = generate_file_loc("ciphers_liboqs.txt")

	# Create cipherlist for liboqs ciphers.
	with open(file_loc) as file:
		data = file.read()

		# Strip trailing newline.
		data_no_trail = data.rstrip('\n')

		# Split for later use.
		data_array = data_no_trail.split(':')

		# Return the definitive list.
		return data_array

def attach():
	"""
	This function runs each of the ciphers as part of the array generated by the generate_ciphers() function, against the server. Sleeps 30 seconds after every cipher.
	"""

	# Generate a list of ciphers.
	cipherlist = generate_ciphers_liboqs()

	# Attach shell to the benchmark-container.
	print("\n[ Attaching shell to benchmark-container] ")
	os.system("docker exec -i -t benchmark-container bash")


if __name__ == "__main__":
	"""
	Main function initialyses the Docker environment, generates a self signed certificate, then starts a SSL/TLS server and finally runs benchmarks for al of these algorithms.
	"""	

	# Run functions.
	initialyse()
	generate_ssc()
	attach()
