IMAGE_NAME = sentiment-ai
PORT = 8080

.PHONY: build run test stop clean tag

build:
	docker build -t $(IMAGE_NAME):latest .

run:
	docker compose up -d --build

test:
	docker run --rm -v "$(CURDIR)":/app -w //app $(IMAGE_NAME):latest pytest tests/ -v --cov=src --cov-report=term-missing

stop:
	docker compose down

clean:
	docker compose down
	docker rmi $(IMAGE_NAME):latest || true

tag:
	git tag -a v0.1.0 -m "Initial SentimentAI release"
	git push origin v0.1.0
