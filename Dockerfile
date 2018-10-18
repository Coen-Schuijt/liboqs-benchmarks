FROM ubuntu:18.04

# Install packages
RUN apt-get update && \
 apt install -qy \
  autoconf \
  automake \
  libtool \
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

# 1
RUN git clone --branch OQS-OpenSSL_1_1_1-stable https://github.com/open-quantum-safe/openssl.git

# 2
RUN git clone --branch master https://github.com/open-quantum-safe/liboqs.git

WORKDIR /usr/local/liboqs-benchmarks/liboqs
RUN autoreconf -i
RUN ./configure --prefix=/usr/local/liboqs-benchmarks/openssl/oqs --enable-shared
RUN make -j
RUN make install

# Install openssl
WORKDIR /usr/local/liboqs-benchmarks/openssl
RUN ./config --prefix=/usr/local/liboqs-benchmarks/openssl -Wl,-rpath -Wl,/usr/local/liboqs-benchmarks/openssl/oqs/lib
RUN make -j

RUN cp libcrypto.so.1.1 ./oqs/lib
RUN cp libssl.so.1.1 ./oqs/lib

# Set working dir to root directory
WORKDIR /usr/local/liboqs-benchmarks
