FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV FREERTOS_KERNEL_PATH=/opt/freertos-kernel

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

# Kernel oficial con el puerto GCC/ARM_CM4F (Cortex-M4, el más común
# en STM32F4/L4). Si usas otra familia (M0/M7), ajusta el puerto al
# compilar — el kernel trae todos los puertos ARM Cortex-M.
RUN git clone --depth 1 \
        https://github.com/FreeRTOS/FreeRTOS-Kernel.git \
        ${FREERTOS_KERNEL_PATH} \
    && cd ${FREERTOS_KERNEL_PATH} \
    && git submodule update --init --depth 1

WORKDIR /workspace/src