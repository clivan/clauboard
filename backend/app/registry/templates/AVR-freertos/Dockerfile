# FreeRTOS en AVR (ATmega). El kernel oficial incluye el puerto AVR_Mega0
# y AVR_AVRDx en su carpeta portable — no requiere un fork especial.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV FREERTOS_KERNEL_PATH=/opt/freertos-kernel

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc-avr \
        avr-libc \
        binutils-avr \
        avrdude \
        make \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 \
        https://github.com/FreeRTOS/FreeRTOS-Kernel.git \
        ${FREERTOS_KERNEL_PATH} \
    && cd ${FREERTOS_KERNEL_PATH} \
    && git submodule update --init --depth 1

WORKDIR /workspace/src