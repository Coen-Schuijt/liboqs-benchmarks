#!/usr/bin/env python3

import os

def initialyse():
	"""
	Function that stops any running docker containers, rebuilds the image from the docker file, creates a local volume and runs the benchmark-container in detached mode. Sets sysctl settings in order to run the benchmarks.
	"""

	# Start docker deamon
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
	os.system("docker volume create benchmark-results-speed")
        os.system("docker volume inspect --format '{{ .Mountpoint }}' benchmark-results-speed > ./.docker_volume_speed.loc")

	# Start the docker container (detached).
	print("\n[ Running docker container ]")
	os.system("docker run --rm -i -t -d --name benchmark-container -v benchmark-results-speed:/usr/local/liboqs-benchmarks/results benchmark-container /bin/bash")

	# Create directory and copy the openssl.cnf file. This makes sure the warning is supressed.
	os.system("docker exec -i -t benchmark-container bash -c 'mkdir -p /usr/local/ssl/ ; cp /etc/ssl/openssl.cnf /usr/local/ssl/openssl.cnf'")

def run_speed():
	"""
	This function initialyses the speedtests and outputs the data to the shared docker volume.
	"""

	# Run tests and output to shared volume.
	print("\n[ Running benchmarks with openssl speed command ]")
	os.system("docker exec -i -t -d benchmark-container bash -c 'openssl/apps/openssl speed oqskem > ./results/openssl-speed_`ls ./results/openssl-speed_* | wc -l`.txt 2>&1'")
	
	return


if __name__ == "__main__":
	"""
	Main function initialyses the Docker environment, then runs speedtest for oqskem algorithms.
	"""	
	
	initialyse()
	run_speed()
