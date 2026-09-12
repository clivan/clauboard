# micro-ROS sobre ESP-IDF (que ya trae FreeRTOS). Se compila desde
# fuente vía micro_ros_setup, siguiendo el mismo patrón que ya usamos
# para ros2-base (no existe paquete apt, es un componente de ESP-IDF).
FROM espressif/idf:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# El componente micro-ROS para ESP-IDF se agrega como un componente
# más del proyecto (no una instalación global) — se clona aquí para
# que ya esté disponible al montar un proyecto nuevo.
RUN git clone -b humble --depth 1 \
        https://github.com/micro-ROS/micro_ros_espidf_component.git \
        /opt/micro_ros_espidf_component

# Uso dentro de un proyecto: copiar o enlazar
# /opt/micro_ros_espidf_component como components/micro_ros_espidf_component
# en la raíz de tu proyecto ESP-IDF antes de `idf.py build`.

WORKDIR /workspace/src