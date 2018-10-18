# liboqs-benchmarks
This repository allows for automated testing of post-quantum crypto algorithms, as well as comparing those against non-post-quantum algorithms. These post-quantum crypto algorithms are based on the [open-quantum-safe/liboqs](https://github.com/open-quantum-safe/liboqs) repo which can be compiled into the [open-quantum-safe/openssl](https://github.com/open-quantum-safe/openssl) repo (based on OpenSSL 1.0.2-stable).

## Prerequisites
In order to run the benchmarks, the following is required:
* docker

If you want to plot the results, the following packages are required:
* pandas
* matplotlib

## Installation
First, clone this repository and move to the respective directory:
```
$ git clone https://github.com/Coen-Schuijt/liboqs-benchmarks.git
$ cd liboqs-benchmarks
```

## Detached Mode [client - server]
The easiest way to perform some benchmarks is by running the docker container in detached mode. This way, the protocols can be benchmarked in a client-server architecture by running the following script:
```
$ sudo ./detached_mode_client_server_liboqs.py
$ sudo ./detached_mode_client_server_generic.py
```

This will create the Docker image from the Dockerfile in the same directory. Also, a shared volume will be created. Within the docker container, two self signed certificates are created: one for non-ECDSA ciphers and one for ECDSA ciphers. Then, two servers are started: one for ECDSA ciphers, one for non-ECDSA ciphers, both with the `s_client` command. Next, for each of the LIBOQS-DEFAULT and LIBOQS-DEFAULT-ECDSA ciphers, the benchmarks are performed by using the `s_time` command.

## Plotting the results
After running one (or multiple) test(s), it is possible to extract and plot the results, generating a .csv file and some graphs. In order to do so, issue the following command:
```
$ ./parse_client_server.py [liboqs | generic]
```

## Attached Mode
When using the attached mode, it is possible to run the `openssl speed` command, or create a client server infrastructure and run the `s_client` or `s_time` command. This is easy for debugging/prototyping or building new features in the detached containers.

## Opening a shell
This is a small shell script to enter a running instance of the benchmark-container, just for your convenience.
