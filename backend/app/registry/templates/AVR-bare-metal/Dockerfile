FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc-avr \
        avr-libc \
        binutils-avr \
        avrdude \
        make \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/src