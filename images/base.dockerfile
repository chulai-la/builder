FROM ubuntu:16.04

RUN echo "deb {{ paas.deb_mirror }} xenial main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-proposed main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-backports main restricted universe multiverse" >> /etc/apt/sources.list

RUN apt-get update -y
RUN apt-get install mariadb-client redis-tools -y
