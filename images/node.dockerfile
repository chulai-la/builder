FROM base:14.04.2

RUN apt-get update -y && apt-get install -y python make build-essential
ADD node-v0.12.4.tar.gz /tmp
RUN cd /tmp/node-v0.12.4 && \
    ./configure && \
    make && \
    make install && \
    rm -rf /tmp/node-v0.12.4*
RUN apt-get clean -y
