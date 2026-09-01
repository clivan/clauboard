FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc-arm-none-eabi \
        libnewlib-arm-none-eabi \
        libstdc++-arm-none-eabi-newlib \
        make \
        cmake \
        git \
        stlink-tools \
        openocd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/src