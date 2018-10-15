FROM ubuntu:18.04

# Install packages
RUN apt-get update && \
 apt install -qy \
  python3 \
  apt-utils \
  gcc \
  make \
  libssl-dev \
  unzip \
  git \
  wget \
  xsltproc

# Setup directories
RUN mkdir -p /usr/local/liboqs-benchmarks && \
  cd /usr/local/liboqs-benchmarks

# Install liboqs
WORKDIR /usr/local/liboqs-benchmarks
RUN git clone https://github.com/open-quantum-safe/liboqs.git
WORKDIR /usr/local/liboqs-benchmarks/liboqs
RUN make

# Install openssl
WORKDIR /usr/local/liboqs-benchmarks
RUN git clone --branch OQS-OpenSSL_1_0_2-stable https://github.com/open-quantum-safe/openssl.git
WORKDIR /usr/local/liboqs-benchmarks/liboqs
RUN make install PREFIX=../openssl/oqs

# Configure OpenSSL
WORKDIR /usr/local/liboqs-benchmarks/openssl
RUN ./Configure linux-x86_64 -lm
RUN make depend
RUN make

# Set working dir to root directory
WORKDIR /usr/local/liboqs-benchmarks
