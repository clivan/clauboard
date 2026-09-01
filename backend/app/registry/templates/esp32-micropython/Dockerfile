# MicroPython para ESP32 requiere el toolchain Xtensa completo de
# ESP-IDF v5+ (no arm-none-eabi) — se parte de la imagen oficial
# de Espressif en vez de instalar un toolchain suelto.
FROM espressif/idf:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        make \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch master \
        https://github.com/micropython/micropython.git /opt/micropython \
    && cd /opt/micropython \
    && make -C mpy-cross

WORKDIR /workspace/src