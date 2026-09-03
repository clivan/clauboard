#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==> AVR bare metal"
docker build -t clauboard/avr-baremetal:latest ./avr-baremetal

echo "==> AVR FreeRTOS"
docker build -t clauboard/avr-freertos:latest ./avr-freertos

echo "==> STM32 bare metal"
docker build -t clauboard/stm32-baremetal:latest ./stm32-baremetal

echo "==> STM32 FreeRTOS"
docker build -t clauboard/stm32-freertos:latest ./stm32-freertos

echo "==> STM32 Zephyr (tarda varios minutos)"
docker build -t clauboard/stm32-zephyr:latest ./stm32-zephyr

echo "==> STM32 MicroPython"
docker build -t clauboard/stm32-micropython:latest ./stm32-micropython

echo "==> ESP32 bare metal"
docker build -t clauboard/esp32-baremetal:latest ./esp32-baremetal

echo "==> ESP32 FreeRTOS (misma imagen que bare metal, ver nota en su Dockerfile)"
docker build -t clauboard/esp32-freertos:latest ./esp32-freertos

echo "==> ESP32 Zephyr (soporte parcial, tarda varios minutos)"
docker build -t clauboard/esp32-zephyr:latest ./esp32-zephyr

echo "==> ESP32 MicroPython"
docker build -t clauboard/esp32-micropython:latest ./esp32-micropython

echo ""
echo "Listo. Imágenes construidas:"
docker images | grep -E "clauboard/(avr|stm32|esp32)-"