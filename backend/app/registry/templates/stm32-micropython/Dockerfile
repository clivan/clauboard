FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

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
        pkg-config \
        libffi-dev \
        stlink-tools \
        dfu-util \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch master \
        https://github.com/micropython/micropython.git /opt/micropython \
    && cd /opt/micropython \
    && make -C mpy-cross \
    && git submodule update --init --depth 1 lib/stm32lib

# Board default: PYBV11. Cambia con BOARD=<nombre> al compilar
# (ver /opt/micropython/ports/stm32/boards/ para las opciones).
ENV MICROPY_BOARD=PYBV11

WORKDIR /workspace/src