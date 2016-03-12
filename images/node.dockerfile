FROM {{ paas.docker_registry }}/base:14.04.3

RUN apt-get update -y && apt-get install -y python make build-essential
ADD node-v4.4.0.tar.gz /tmp
RUN cd /tmp/node-v4.4.0 && \
    ./configure && \
    make && \
    make install && \
    rm -rf /tmp/node-v4.4.0*
RUN apt-get clean -y
