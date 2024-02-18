FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_PREFER_BINARY=1 \
    CUDA_HOME=/usr/local/cuda-11.8 \
    DEBCONF_NOWARNINGS=yes
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y \
        poppler-utils \
        libpoppler-dev \
        wget \
        curl \
        git \
        python3-dev \
        python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

WORKDIR /app

RUN pip install \
        torch \
        torchvision \
        --index-url https://download.pytorch.org/whl/cu118 \
    && pip install opencv-python-headless \
        networkx \
        transformers==4.30 \
        sentencepiece \
        pdf2image \
        fastapi[uvicorn] \
        uvicorn \
        PyPDF2 \
        matplotlib \
        timm \
        scipy \
        shapely \
        pyclipper \
        scikit-image \
        python-multipart \
        onnxruntime \
        requests \
        gradio \
        Pillow==8.4.0 \
        blobfile \
        mypy \
        numpy \
        pytest \
        einops \
        tensorboard \
        opencv-python==4.5.1.48 \
        Shapely==1.8.4 

RUN pip install \
        "git+https://github.com/facebookresearch/detectron2.git"

RUN git clone https://github.com/microsoft/unilm.git /unilm \
        && sed -i 's/from collections import Iterable/from collections.abc import Iterable/' \
        /unilm/dit/object_detection/ditod/table_evaluation/data_structure.py

ADD . /app/