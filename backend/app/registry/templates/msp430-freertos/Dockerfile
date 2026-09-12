# FreeRTOS en MSP430. TI mantiene una demo oficial documentada en
# freertos.org para MSP430FR5969 (16-bit core) — el kernel oficial
# incluye el puerto correspondiente en su carpeta portable.
FROM cdelledonne/msp430-gcc:latest

ENV FREERTOS_KERNEL_PATH=/opt/freertos-kernel

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 \
        https://github.com/FreeRTOS/FreeRTOS-Kernel.git \
        ${FREERTOS_KERNEL_PATH} \
    && cd ${FREERTOS_KERNEL_PATH} \
    && git submodule update --init --depth 1

WORKDIR /workspace/src