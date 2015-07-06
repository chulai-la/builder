FROM {{ paas.docker_registry }}/base:14.04.2

RUN apt-get update -y && apt-get install -y python make build-essential
ADD node-v0.12.6.tar.gz /tmp
RUN cd /tmp/node-v0.12.6 && \
    ./configure && \
    make && \
    make install && \
    rm -rf /tmp/node-v0.12.6*
RUN apt-get clean -y
