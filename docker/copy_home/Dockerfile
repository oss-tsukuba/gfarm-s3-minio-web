FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install inotify-tools rsync dumb-init

COPY inotify_copy.sh /inotify_copy.sh
STOPSIGNAL 15

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/inotify_copy.sh", "1800"]
