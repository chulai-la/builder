FROM {{ paas.docker_registry }}/node:4.4.0

RUN apt-get update -y
RUN apt-get install -y

RUN useradd -m -d /home/{{ paas.user }} -s /bin/bash -u {{ paas.uid }} {{ paas.user }}
RUN sudo apt-get install -y autoconf bison build-essential libssl-dev libyaml-dev libreadline6-dev zlib1g-dev libncurses5-dev libffi-dev libgdbm3 libgdbm-dev git curl libmysql++-dev libsqlite3-dev

USER {{ paas.user }}
RUN git clone https://github.com/sstephenson/ruby-build.git /home/{{ paas.user }}/ruby-build
RUN export RUBY_BUILD_MIRROR_URL={{ paas.ruby_build_mirror }} && /home/{{ paas.user }}/ruby-build/bin/ruby-build 2.3.0 /home/{{ paas.user }}/.ruby-2.3.0
ENV PATH=/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/bin:/usr/local/sbin:/home/{{ paas.user }}/.ruby-2.3.0/bin
RUN gem sources --remove https://rubygems.org/; \
    gem sources -a {{ paas.gem_mirror }}; \
    gem install bundle
