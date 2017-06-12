FROM ubuntu:16.04

RUN echo "deb {{ paas.deb_mirror }} trusty main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} trusty-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} trusty-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} trusty-proposed main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} trusty-backports main restricted universe multiverse" >> /etc/apt/sources.list

RUN apt-get update -y
RUN apt-get install mariadb-client redis-tools -y
