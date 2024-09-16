NAME=pdf-translator
TAG=0.1.0
PROJECT_DIRECTORY=$(shell pwd)
MODEL_FILE=models/unilm/publaynet_dit-b_cascade.pth

build:
	mkdir -p models/unilm 
	if [ ! -f $(MODEL_FILE) ]; then \
		wget "https://huggingface.co/Sebas6k/DiT_weights/resolve/main/publaynet_dit-b_cascade.pth?download=true" -P models/unilm -O publaynet_dit-b_cascade.pth; \
	fi

	docker build -t ${NAME}:${TAG} .

get_models:
	if [ ! -f $(MODEL_FILE) ]; then \
		wget "https://huggingface.co/Sebas6k/DiT_weights/resolve/main/publaynet_dit-b_cascade.pth?download=true" -P models/unilm -O publaynet_dit-b_cascade.pth; \
	fi

run:
	docker run -it \
		--runtime=nvidia \
		--name pdf-translator \
		-v ${PROJECT_DIRECTORY}:/app \
		--gpus all \
		-p 8765:8765 \
		${NAME}:${TAG}

run-bash:
	docker run -it \
		--runtime=nvidia \
		--name pdf-translator \
		-v ${PROJECT_DIRECTORY}:/app \
		--gpus all \
		-p 8765:8765 \
		${NAME}:${TAG} /bin/bash
