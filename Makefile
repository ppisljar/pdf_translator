NAME=pdf-translator
TAG=0.1.0
PROJECT_DIRECTORY=$(shell pwd)
MODEL_FILE=models/unilm/publaynet_dit-b_cascade.pth

build:
	mkdir -p models/unilm 
	if [ ! -f $(MODEL_FILE) ]; then \
		wget "https://layoutlm.blob.core.windows.net/dit/dit-fts/publaynet_dit-b_cascade.pth?sv=2022-11-02&ss=b&srt=o&sp=r&se=2033-06-08T16:48:15Z&st=2023-06-08T08:48:15Z&spr=https&sig=a9VXrihTzbWyVfaIDlIT1Z0FoR1073VB0RLQUMuudD4%3D" -P models/unilm -O publaynet_dit-b_cascade.pth; \
	fi

	docker build -t ${NAME}:${TAG} .

get_models:
	if [ ! -f $(MODEL_FILE) ]; then \
		wget "https://layoutlm.blob.core.windows.net/dit/dit-fts/publaynet_dit-b_cascade.pth?sv=2022-11-02&ss=b&srt=o&sp=r&se=2033-06-08T16:48:15Z&st=2023-06-08T08:48:15Z&spr=https&sig=a9VXrihTzbWyVfaIDlIT1Z0FoR1073VB0RLQUMuudD4%3D" -P models/unilm -O publaynet_dit-b_cascade.pth; \
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
