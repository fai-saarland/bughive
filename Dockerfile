FROM ubuntu:noble
RUN mkdir docker
WORKDIR \docker
RUN apt-get update && apt-get install -y python3 python3-pip python-is-python3 python3-venv python3-wheel git wget build-essential gcc g++ clang make cmake vim valgrind gdb coreutils automake bison flex unzip curl zip tar pkg-config autoconf libtool libboost-all-dev libssl-dev libre2-dev gringo libgrpc-dev protobuf-compiler-grpc libgrpc++-dev
# install dynet for cppdl ASNets
RUN mkdir eigen && cd eigen && wget https://github.com/clab/dynet/releases/download/2.1/eigen-b2e267dc99d4.zip && unzip eigen-b2e267dc99d4.zip && rm eigen-b2e267dc99d4.zip && cd ..
RUN git clone https://github.com/clab/dynet.git && cd dynet && mkdir build && cd build && cmake .. -DEIGEN3_INCLUDE_DIR=/docker/eigen && make -j 8 && make install && cd /docker
# install dependencies for GNN policy server
# since we are only generating a docker image, we do not use a virtual environment here 
RUN pip install termcolor torch pytorch_lightning tarski grpcio protobuf --break-system-packages
# shallow clone of bughive repository, only clone one level of submodules (excludes cppdl-test repository)
# in case you plan to not just use the framework but actually implement something, consider cloning it normally
RUN cd /docker && git clone --depth 1 https://github.com/fai-saarland/bughive.git && cd bughive && git submodule update --init --depth 1
# build Aras for aras oracle
RUN cd /docker/bughive/fd-action-policy-testing/resources && unzip aras.zip -d aras && cd aras/src && ./build_all && cd ../../ && rm aras.zip
# build bughive components
RUN cd /docker/bughive && echo "DYNET_ROOT = /usr/local" > Makefile.config && make all
