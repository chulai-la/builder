FROM hello:latest

RUN mkdir -p /home/usr/deps && \
    cd /home/usr/deps && \
    rm -f pkgs.list propose.list && \
    touch installed.list && \
    echo tmux >> propose.list && \
    echo vim >> propose.list && \
    echo nmon >> propose.list && \
    grep -F -x -v -f installed.list propose.list | sort > pkgs.list && \
    if [ -s pkgs.list ]; then \
        echo "installing extra libs" `cat pkgs.list | tr "\\n" " "` && apt-get update -y && apt-get install -y `cat pkgs.list`; \
    fi && \
    cat pkgs.list installed.list | sort | uniq > installed.list.new && \
    mv installed.list.new installed.list && \
    rm -f pkgs.list propose.list

