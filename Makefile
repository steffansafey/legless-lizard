# Project
NAME = legless-lizard
PACKAGE = ll

# Environment
PWD = $(shell pwd)

# AWS
include ./secrets.env

# Docker
IMAGE_NAME = 790542884824.dkr.ecr.us-east-1.amazonaws.com/$(NAME)
IMAGE_TAG_BASE=base-latest
IMAGE_TAG_DEV=dev-latest
IMAGE_TAG_PROD=latest

# Application
LOG_LEVEL = INFO
TEST_PATH = legless-lizard/tests

# Docs
.DEFAULT_GOAL := help

help:
	@python3 make_makefile_docs.py $(NAME)

## Build the development image
build: build-base build-dev prune

## Build the base Docker image - used in CI only
build-base:
	DOCKER_BUILDKIT=1 \
	docker build \
	--build-arg BASE_IMAGE=$(IMAGE_NAME):$(IMAGE_TAG_BASE) \
	--build-arg CODE_ARTIFACT_TOKEN=$(CODE_ARTIFACT_TOKEN) \
	-t $(IMAGE_NAME):$(IMAGE_TAG_BASE) \
	-f docker/Dockerfile \
	--target=base \
	.

## Build the development Docker image
build-dev:
	DOCKER_BUILDKIT=1 \
	docker build \
	--build-arg BASE_IMAGE=$(IMAGE_NAME):$(IMAGE_TAG_BASE) \
	--build-arg CODE_ARTIFACT_TOKEN=$(CODE_ARTIFACT_TOKEN) \
	-t $(IMAGE_NAME):$(IMAGE_TAG_DEV) \
	-f docker/Dockerfile \
	--target=dev \
	.

## Build the production Docker image
build-prod:
	DOCKER_BUILDKIT=1 \
	docker build \
	--build-arg BASE_IMAGE=$(IMAGE_NAME):$(IMAGE_TAG_BASE) \
	--build-arg CODE_ARTIFACT_TOKEN=$(CODE_ARTIFACT_TOKEN) \
	-t $(IMAGE_NAME):$(IMAGE_TAG_PROD) \
	-f docker/Dockerfile \
	--target=prod \
	.

## Run application in development mode
run: run-web

# Download launch.json configuration for vscode
.vscode/launch.json:
	mkdir -p .vscode
	curl -s https://gitlab.com/-/snippets/2304427/raw/main/vscode_python_debug_launch_config.json | sed -e 's/REPO_NAME/$(NAME)/g' > .vscode/launch.json

## Add libraries to pypoetry.toml - make add-libs LIBS="first second@6.2"
add-libs:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
    docker compose \
    --project-directory . \
    -f docker/docker-compose.yml \
    run \
    -v $(PWD)/pyproject.toml:/$(NAME)/pyproject.toml \
    -v $(PWD)/poetry.lock:/$(NAME)/poetry.lock \
    dev add $(LIBS)

## Update libraries according to versions in pyproject.toml
update-libs:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
    docker compose \
    --project-directory . \
    -f docker/docker-compose.yml \
    run \
    -v $(PWD)/pyproject.toml:/$(NAME)/pyproject.toml \
    -v $(PWD)/poetry.lock:/$(NAME)/poetry.lock \
    dev update


# run-dev:
# 	IMAGE_TAG=$(IMAGE_TAG_DEV) \
# 	docker-compose \
# 	--project-directory . \
# 	-f docker/docker-compose.yml \
# 	up -d dev

lock:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
    docker compose \
    --project-directory . \
    -f docker/docker-compose.yml \
    run \
    -v $(PWD)/pyproject.toml:/$(NAME)/pyproject.toml \
    -v $(PWD)/poetry.lock:/$(NAME)/poetry.lock \
    dev bash -c "poetry lock --no-update"

## Run API in development mode
run-web:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
	LOG_LEVEL=$(LOG_LEVEL) \
	docker-compose \
	--project-directory . \
	-f docker/docker-compose.yml \
	up -d web


## Stop all services and prune Docker resources
down:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
	docker-compose \
	--project-directory . \
	-f docker/docker-compose.yml \
	down


## Restart application
restart: stop run

## Show Docker logs for all container services
logs:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
	docker-compose \
	--project-directory . \
	-f docker/docker-compose.yml \
	logs \
	--follow

## Run unit tests - set `TEST_PATH` for specific tests
test:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
	docker-compose \
	--project-directory . \
	-f docker/docker-compose.yml \
	run \
	--rm \
	dev test $(TEST_PATH)


## Run style checks
lint:
	docker run \
	--rm \
	-v $(PWD)/$(PACKAGE):/$(NAME)/$(PACKAGE)/ \
	-v $(PWD)/scripts:/$(NAME)/scripts \
	$(IMAGE_NAME):$(IMAGE_TAG_DEV) \
	lint

## Run code formatters
fmt:
	docker run \
	--rm \
	-v $(PWD)/$(PACKAGE):/$(NAME)/$(PACKAGE)/ \
	-v $(PWD)/scripts:/$(NAME)/scripts \
	$(IMAGE_NAME):$(IMAGE_TAG_DEV) \
	fmt

## Open a bash shell inside the dev container
bash:
	docker run \
	-it \
	--rm \
	-v $(PWD)/$(PACKAGE):/$(NAME)/$(PACKAGE)/ \
	-v $(PWD)/scripts:/$(NAME)/scripts \
	$(IMAGE_NAME):$(IMAGE_TAG_DEV) \
	bash

## Prune Docker containers, volumes, networks, and images
prune:
	docker container prune -f && \
	docker volume prune -f && \
	docker network prune -f && \
	docker image prune -f
## Run database revision - `REVISION_NAME` required
revision:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
	docker-compose \
	--project-directory . \
	-f docker/docker-compose.yml \
	run \
	--rm \
	api revision $(REVISION_NAME)

## Run migration for the latest revision
migrate:
	IMAGE_NAME=$(IMAGE_NAME) \
	IMAGE_TAG=$(IMAGE_TAG_DEV) \
	docker-compose \
	--project-directory . \
	-f docker/docker-compose.yml \
	run \
	--rm \
	api migrate
