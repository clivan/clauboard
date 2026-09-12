# Pico 2 (RP2350) — FreeRTOS + Pico SDK, básico (ARM únicamente).
# NOTA: template "por si acaso" — probado hasta compilar el kernel,
# no se armaron ejemplos propios. Cuando lo necesites de verdad,
# probablemente valga la pena revisar y ampliar este Dockerfile.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PICO_SDK_PATH=/opt/pico-sdk
ENV FREERTOS_KERNEL_PATH=/opt/freertos-kernel
ENV PICO_PLATFORM=rp2350-arm-s

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
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

# Kernel oficial de FreeRTOS con soporte SMP (el que documenta
# freertos.org para Pico)
RUN git clone --depth 1 \
        https://github.com/FreeRTOS/FreeRTOS-Kernel.git \
        ${FREERTOS_KERNEL_PATH} \
    && cd ${FREERTOS_KERNEL_PATH} \
    && git submodule update --init --depth 1

WORKDIR /workspace/src