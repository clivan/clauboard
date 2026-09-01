# Zephyr en ESP32: soporte funcional pero con reservas según el propio
# proyecto Zephyr (issue de tracking sigue abierto). Wifi/Bluetooth y
# algunos periféricos pueden no estar completamente soportados según
# la variante exacta de ESP32 (original / S2 / S3 / C3).
# Ver: https://github.com/zephyrproject-rtos/zephyr/issues/29394
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

# Zephyr necesita el toolchain Xtensa específico de Espressif además
# del SDK genérico de Zephyr — se instala vía su propio gestor.
RUN west espressif update 2>/dev/null || true

WORKDIR /workspace/src