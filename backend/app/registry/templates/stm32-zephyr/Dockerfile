# Zephyr para STM32 — ST contribuye activamente a Zephyr y lo soporta
# oficialmente en producción (STM32U5, F4, L4, etc. según el board).
FROM ubuntu:22.04

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
        stlink-tools \
        openocd \
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