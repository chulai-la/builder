FROM ubuntu:16.04

RUN echo "deb {{ paas.deb_mirror }} xenial main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-proposed main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb {{ paas.deb_mirror }} xenial-backports main restricted universe multiverse" >> /etc/apt/sources.list

RUN apt-get update -y
RUN apt-get install mysql-client redis-tools curl vim tmux nmon htop sl cowsay tree tig autossh apt-transport-https -y
RUN rm -rf /var/cache/apt && apt-get clean -y
