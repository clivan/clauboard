
# Pico 2 (RP2350) — bare metal, C/C++ Pico SDK, arquitectura ARM (Cortex-M33)
FROM ubuntu:22.04
 
ENV DEBIAN_FRONTEND=noninteractive
ENV PICO_SDK_PATH=/opt/pico-sdk
ENV PICO_PLATFORM=rp2350-arm-s
 
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        cmake \
        build-essential \
        gcc-arm-none-eabi \
        libnewlib-arm-none-eabi \
        libstdc++-arm-none-eabi-newlib \
        python3 \
        picotool \
    && rm -rf /var/lib/apt/lists/*
 
RUN git clone --depth 1 --branch master \
        https://github.com/raspberrypi/pico-sdk.git ${PICO_SDK_PATH} \
    && cd ${PICO_SDK_PATH} \
    && git submodule update --init --depth 1
 
WORKDIR /workspace/src