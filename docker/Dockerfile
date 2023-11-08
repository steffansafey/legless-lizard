ARG BASE_IMAGE

FROM python:3.10-slim-bullseye AS base

ARG CODE_ARTIFACT_TOKEN

ENV POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /legless-lizard

RUN set -x \
  && apt-get update \
  && apt-get install -y curl gcc libpq-dev git

# Install poetry (respects above environment variables)
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* ./

# Install libraries (including SF libraries)
COPY ./scripts/run_libs_install.sh ./scripts/run_libs_install.sh
RUN ./scripts/run_libs_install.sh

FROM base as dev

RUN poetry install --with dev

COPY docker/entrypoint.sh /usr/local/bin

COPY alembic.ini  ./
COPY ll ./ll
COPY scripts ./scripts

ENTRYPOINT ["entrypoint.sh"]

FROM ${BASE_IMAGE} as prod-base

FROM python:3.10-slim-bullseye as prod

ARG BUILD_VERSION

WORKDIR /legless-lizard

COPY --from=prod-base /usr/local /usr/local

# Bake BUILD_VERSION environment variable into the image
ENV BUILD_VERSION ${BUILD_VERSION}

COPY docker/entrypoint.sh /usr/local/bin

COPY alembic.ini ./
COPY ll ./ll
COPY scripts ./scripts

ENTRYPOINT ["entrypoint.sh"]
