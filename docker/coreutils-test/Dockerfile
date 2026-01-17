FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        coreutils \
        locales \
        man-db \
        manpages \
        manpages-posix \
        manpages-posix-dev \
        groff-base && \
    yes | unminimize && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY setup_test_fixtures.sh /usr/local/bin/setup_coreutils_fixtures.sh
RUN chmod +x /usr/local/bin/setup_coreutils_fixtures.sh && \
    /usr/local/bin/setup_coreutils_fixtures.sh

ENV COREUTILS_FIXTURES_DIR=/opt/coreutils-fixtures


