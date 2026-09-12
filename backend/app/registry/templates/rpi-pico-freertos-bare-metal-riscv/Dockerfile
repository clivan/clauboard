# Pico 2 (RP2350) — bare metal, C/C++ Pico SDK, arquitectura RISC-V (Hazard3)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PICO_SDK_PATH=/opt/pico-sdk
ENV PICO_PLATFORM=rp2350-riscv
ENV PICO_TOOLCHAIN_PATH=/opt/riscv/riscv-toolchain-14

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        cmake \
        build-essential \
        python3 \
        python3-dev \
        curl \
        picotool \
    && rm -rf /var/lib/apt/lists/*

# Toolchain oficial RISC-V de Raspberry Pi (no hay paquete apt para esto,
# se descarga el binario oficial del propio proyecto pico-sdk-tools)
RUN mkdir -p ${PICO_TOOLCHAIN_PATH} \
    && curl -fsSL \
        https://github.com/raspberrypi/pico-sdk-tools/releases/download/v2.0.0-5/riscv-toolchain-14-x86_64-lin.tar.gz \
        -o /tmp/riscv-toolchain.tar.gz \
    && tar xzf /tmp/riscv-toolchain.tar.gz -C ${PICO_TOOLCHAIN_PATH} \
    && rm /tmp/riscv-toolchain.tar.gz

RUN git clone --depth 1 --branch master \
        https://github.com/raspberrypi/pico-sdk.git ${PICO_SDK_PATH} \
    && cd ${PICO_SDK_PATH} \
    && git submodule update --init --depth 1

WORKDIR /workspace/src