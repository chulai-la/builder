FROM {{ paas.docker_registry }}/base:16.04

ADD node-v6.11.0-linux-x64.tar.xz /usr/local/node
ENV PATH /usr/local/node/bin:$PATH

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update -y && apt-get install -y yarn
RUN apt-get clean -y
