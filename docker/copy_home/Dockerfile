FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install inotify-tools rsync

COPY inotify_copy.sh /inotify_copy.sh

ENTRYPOINT ["/inotify_copy.sh"]
