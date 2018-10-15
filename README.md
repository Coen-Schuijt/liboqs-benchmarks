# liboqs-benchmarks
This repository allows for automated testing of post-quantum crypto algorithms, as well as comparing those against non-post-quantum algorithms. These post-quantum crypto algorithms are based on the [open-quantum-safe/liboqs](https://github.com/open-quantum-safe/liboqs) repo which can be compiled into the [open-quantum-safe/openssl](https://github.com/open-quantum-safe/openssl) repo (based on OpenSSL 1.0.2-stable).

## Prerequisites
In order to run the benchmarks, the following is required:
* docker

## Installation
First, clone this repository and move to the respective directory:
```
$ git clone https://github.com/Coen-Schuijt/liboqs-benchmarks.git
$ cd liboqs-benchmarks
```

## Detached Mode
The easiest way to perform some benchmarks is by running the docker container in detached mode. The detached container is available in two flavours: detached_speed and detached_client_server.

### Detached_speed
The detached_speed container is setting up the environment and running the `openssl speed` command in a controlled environment. To run the ssl peed benchmarks in detached mode, run the following command:
```
$ sudo ./detached_mode_speed.py
```
This will create the Docker image from the Dockerfile in the same directory. Also, a shared volume will be created. Then the `openssl speed oqskem` command is executed. The output is stored in the shared volume. 

During the benchmark, the the results can be monitored **as root user** by using the following commands, where $i is the number of the benchmark (in case you run more than once):
```
$ cd /var/lib/docker/volumes/benchmark-results/_data/
$ ls -l
$ tail -f openssl-speed_$i.txt 
```

### Detached_client_server
Instead of running the `openssl speed oqskem' command, the protocols can be benchmarked in a client-server architecture by running the following script:
```
$ sudo ./detached_mode_client_server_liboqs.py
$ sudo ./detached_mode_client_server_generic.py
```

This will create the Docker image from the Dockerfile in the same directory. Also, a shared volume will be created. Within the docker container, two self signed certificates are created: one for non-ECDSA ciphers and one for ECDSA ciphers. Then, two servers are started: one for ECDSA ciphers, one for non-ECDSA ciphers, both with the `s_client` command. Next, for each of the LIBOQS-DEFAULT and LIBOQS-DEFAULT-ECDSA ciphers, the benchmarks are performed by using the `s_time` command.

The results for the benchmarks can be monitored **as root user** by using the following commands, where $CIPHER is the respective cipher and $i is the number of the benchmark (in case you run more than once):
```
$ cd /var/lib/docker/volumes/benchmark-results/_data/
$ ls -l
$ tail -f s-time_$CIPHER_$i.txt
```

## Attached Mode
When using the attached mode, it is possible to run the `openssl speed` command, or create a client server infrastructure and run the `s_client` or `s_time` command. This is easy for debugging/prototyping or building new features in the detached containers.

### Running openssl speed
To run the `openssl speed` command, first start the docker container by running the following command.
```
$ sudo ./attached_mode.py 
```
This will create the Docker image from the Dockerfile in the same directory. Also, a shared volume will be created. The necessary certificates will be generated as well. When running the container in attached mode, a shell is opened once the container is launched.  In order to run the `openssl speed` benchmarks and output the results in the shared volume, run the following command within the container:
```
$ openssl/apps/openssl speed oqskem > ./results/openssl-speed_`ls ./results/openssl-speed_* | wc -l`.txt 2>&1
```

During the benchmark, the the results can be monitored **as root user** by using the following commands, where $i is the number of the benchmark (in case you run more than once):
```
$ cd /var/lib/docker/volumes/benchmark-results/_data/
$ ls -l
$ tail -f openssl-speed_$i.txt 
```

## Client-Server benchmark
After running the `./attached_mode.sh` script, you end up with a shell. By executing the following steps in order, it is possible to run the `s_time` benchmarks benchmarks. When launching the container two self signed certificate are created. The ciphers in liboqs can be categorized into two groups: those based on RSA and those based on ECDSA. Below, the RSA group is refered to as non-ECDSA. 

### Start the server (non-ECDSA)
In order to start the server to connect with non-ECDSA ciphers, issue the following command:
```
$ openssl/apps/openssl s_server -accept 4444 -cipher OQSKEM-DEFAULT:OQSKEM-DEFAULT-ECDHE -cert server-rsa-cert.pem
```

### Start the client/s_time benchmark (non-ECDSA)
In order to start the tests within the same docker container, start a new terminal instance (or tab, for that matter). Next, run the `connect.py` script to create a new bash session within the container:
```
$ sudo ./shell.py
```

Next, to run the `openssl s_client` application (non-ECDSA), run the following command:
```
$ openssl/apps/openssl s_client -connect localhost:4444 -cipher OQSKEM-DEFAULT -cert server-rsa-cert.pem
```

To run the `openssl s_time` benchmarks (non-ECDSA), run the following command:
```
$ openssl/apps/openssl s_time -connect localhost:4444 -cipher OQSKEM-DEFAULT -cert server-rsa-cert.pem > ./results/s-time_OQSKEM-DEFAULT-CIPHER_`ls ./results/s-time_OQSKEM-DEFAULT-CIPHER_* | wc -l`.txt 2>&1
```

To generate an overview of the available ciphers, run the following command:
```
$ openssl/apps/openssl ciphers OQSKEM-DEFAULT
```

---

### Start the server (ECDSA)
In order to start the server to connect with ECDSA ciphers, issue the following command:
```
$ openssl/apps/openssl s_server -accept 5555 -cipher OQSKEM-DEFAULT:OQSKEM-DEFAULT-ECDHE -cert ecdsa.cert -key ecdsa.key
```

### Start the client/s_time benchmark (ECDSA)
In order to start the tests within the same docker container, start a new terminal instance (or tab, for that matter). Next, run the `connect.py` script to create a new bash session within the container:
```
$ sudo ./shell.py
```

Next, to run the `openssl s_client` application (ECDSA), run the following command:
```
$ openssl/apps/openssl s_client -connect localhost:5555 -cipher OQSKEM-DEFAULT-ECDHE -cert ecdsa.cert -key ecdsa.key
```

To run the `openssl s_time` benchmarks (ECDSA), run the following command:
```
$ openssl/apps/openssl s_time -connect localhost:5555 -cipher OQSKEM-DEFAULT-ECDHE -cert ecdsa.cert -key ecdsa.key > ./results/s-time_OQSKEM-DEFAULT-ECDHE-CIPHER_`ls ./results/s-time_OQSKEM-DEFAULT-ECDHE-CIPHER_* | wc -l`.txt 2>&1
```

To generate an overview of the available ECDSA ciphers, run the following command:
```
$ openssl/apps/openssl ciphers OQSKEM-DEFAULT-ECDHE
```
