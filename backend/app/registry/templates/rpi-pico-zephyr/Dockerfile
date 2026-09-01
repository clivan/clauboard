# Pico 2 (RP2350) — Zephyr RTOS, básico (ARM únicamente).
# NOTA: template "por si acaso" — Zephyr usa su propio gestor de
# dependencias (west) y es bastante más pesado que los otros
# frameworks (~2-3GB de build). Cuando lo necesites de verdad,
# vale la pena revisar https://github.com/raspberrypi/pico-zephyr
# para ejemplos ya armados en vez de partir de cero con esto.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        cmake \
        ninja-build \
        gperf \
        ccache \
        dfu-util \
        device-tree-compiler \
        wget \
        python3 \
        python3-pip \
        python3-venv \
        xz-utils \
        file \
        gcc-arm-none-eabi \
        libnewlib-arm-none-eabi \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/zephyrproject/.venv
ENV PATH="/opt/zephyrproject/.venv/bin:${PATH}"

RUN pip install --no-cache-dir west

RUN west init /opt/zephyrproject \
    && cd /opt/zephyrproject \
    && west update --narrow -o=--depth=1

RUN pip install --no-cache-dir \
        -r /opt/zephyrproject/zephyr/scripts/requirements.txt

WORKDIR /workspace/src