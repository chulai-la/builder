FROM {{ paas.docker_registry }}/base:16.04

ADD node-v6.11.0-linux-x64.tar.xz /usr/local/node
ENV PATH /usr/local/node/bin:$PATH
