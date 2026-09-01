FROM clauboard/ros2-base:humble

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-realsense2-camera \
    librealsense2-utils \
    librealsense2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
