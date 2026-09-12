# OpenCV completo: core + contrib + CUDA + DNN acelerado, con
# bindings de Python Y headers de C++ en la misma imagen.
#
# CUDA_ARCH_BIN=8.6 es específico para RTX 30xx (confirmado para
# RTX 3050). Si algún día usas esta imagen con otra GPU, ajusta:
#   RTX 40xx = 8.9 | RTX 30xx = 8.6 | RTX 20xx = 7.5 | GTX 16xx = 7.5
#
# Compila desde fuente (no hay wheel de pip con CUDA) — tarda entre
# 20 y 60 minutos según CPU. Requiere NVIDIA Container Toolkit
# instalado en el HOST para que el contenedor vea la GPU en runtime
# (verificar con: docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
# ANTES de construir esta imagen).

FROM nvidia/cuda:12.3.2-cudnn9-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV OPENCV_VERSION=4.10.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        pkg-config \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libgtk-3-dev \
        libatlas-base-dev \
        gfortran \
        python3 \
        python3-dev \
        python3-pip \
        python3-numpy \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Fuente de OpenCV + contrib, misma versión en ambos (requisito,
# versiones distintas entre core y contrib no compilan)
RUN git clone --branch ${OPENCV_VERSION} --depth 1 \
        https://github.com/opencv/opencv.git /opt/opencv \
    && git clone --branch ${OPENCV_VERSION} --depth 1 \
        https://github.com/opencv/opencv_contrib.git /opt/opencv_contrib

WORKDIR /opt/opencv/build

RUN cmake \
        -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib/modules \
        -D OPENCV_ENABLE_NONFREE=ON \
        -D WITH_CUDA=ON \
        -D WITH_CUDNN=ON \
        -D OPENCV_DNN_CUDA=ON \
        -D CUDA_ARCH_BIN=8.6 \
        -D ENABLE_FAST_MATH=ON \
        -D CUDA_FAST_MATH=ON \
        -D WITH_CUBLAS=ON \
        -D WITH_CUFFT=ON \
        -D WITH_GSTREAMER=ON \
        -D WITH_V4L=ON \
        -D WITH_TBB=ON \
        -D PYTHON3_EXECUTABLE=/usr/bin/python3 \
        -D PYTHON3_NUMPY_INCLUDE_DIRS=/usr/lib/python3/dist-packages/numpy/core/include \
        -D BUILD_EXAMPLES=OFF \
        -D BUILD_TESTS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        .. \
    && make -j$(nproc) \
    && make install \
    && ldconfig

WORKDIR /workspace/src