NAME=pdf-translator
TAG=0.1.0
PROJECT_DIRECTORY=$(shell pwd)/..

build:
	mkdir -p /app/models/unilm \
			&& wget "https://layoutlm.blob.core.windows.net/dit/dit-fts/publaynet_dit-b_cascade.pth?sv=2022-11-02&ss=b&srt=o&sp=r&se=2033-06-08T16:48:15Z&st=2023-06-08T08:48:15Z&spr=https&sig=a9VXrihTzbWyVfaIDlIT1Z0FoR1073VB0RLQUMuudD4%3D" -P /app/models/unilm -O publaynet_dit-b_cascade.pth

	docker build -t ${NAME}:${TAG} .

run:
	docker run -it \
		--runtime=nvidia \
		--name pdf-translator \
		-v ${PROJECT_DIRECTORY}:/app \
		--gpus all \
		-d --restart=always \
		-p 8765:8765 \
		-p 8288:8288 \
		${NAME}:${TAG} /bin/bash -c "python3 server.py"

run-bash:
	docker run -it \
		--runtime=nvidia \
		--name pdf-translator \
		-v ${PROJECT_DIRECTORY}:/app \
		--gpus all \
		-d --restart=always \
		-p 8765:8765 \
		-p 8288:8288 \
		${NAME}:${TAG} /bin/bash
