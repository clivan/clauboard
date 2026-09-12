# Pico 2 (RP2350) — entorno para compilar firmware MicroPython custom
# (con tus propios módulos en C, o para flashear el .uf2 oficial ya compilado)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PICO_SDK_PATH=/opt/pico-sdk

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        cmake \
        build-essential \
        gcc-arm-none-eabi \
        libnewlib-arm-none-eabi \
        libstdc++-arm-none-eabi-newlib \
        python3 \
        python3-pip \
        python3-dev \
        pkg-config \
        libffi-dev \
        picotool \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch master \
        https://github.com/raspberrypi/pico-sdk.git ${PICO_SDK_PATH} \
    && cd ${PICO_SDK_PATH} \
    && git submodule update --init --depth 1

RUN git clone --depth 1 --branch master \
        https://github.com/micropython/micropython.git /opt/micropython \
    && cd /opt/micropython \
    && make -C mpy-cross \
    && git submodule update --init --depth 1 lib/pico-sdk lib/tinyusb

WORKDIR /workspace/src