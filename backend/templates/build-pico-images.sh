#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==> rpi-pico bare metal ARM"
docker build -t clauboard/rpi-pico-baremetal-arm:latest ./rpi-pico-baremetal-arm

echo "==> rpi-pico bare metal RISC-V"
docker build -t clauboard/rpi-pico-baremetal-riscv:latest ./rpi-pico-baremetal-riscv

echo "==> rpi-pico MicroPython (ARM base — el flag PICO_PLATFORM se pasa en build de MicroPython, no de la imagen)"
docker build -t clauboard/rpi-pico-micropython-arm:latest ./rpi-pico-micropython
docker tag clauboard/rpi-pico-micropython-arm:latest clauboard/rpi-pico-micropython-riscv:latest

echo "==> rpi-pico FreeRTOS (básico, solo ARM)"
docker build -t clauboard/rpi-pico-freertos:latest ./rpi-pico-freertos

echo "==> rpi-pico Zephyr (básico, solo ARM — tarda varios minutos)"
docker build -t clauboard/rpi-pico-zephyr:latest ./rpi-pico-zephyr

echo "Listo:"
docker images | grep clauboard/rpi-pico