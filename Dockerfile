ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG AS base

# add bash, because it's not available by default on alpine
RUN apk add --no-cache bash

WORKDIR /app/

# install poetry
COPY ./requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install -r ./requirements.txt

# create new environment
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yaml ./environment.yaml
RUN --mount=type=cache,target=/opt/conda/pkgs \
    conda env create -f ./environment.yaml

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "certifier", "/bin/bash", "-c"]

WORKDIR /app/certifier/

# add poetry files
COPY ./certifier/pyproject.toml ./certifier/poetry.lock ./

FROM base AS test

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main,test

# add source, tests and necessary files
COPY ./certifier/src/ ./src/
COPY ./certifier/tests/ ./tests/
COPY ./certifier/LICENSE ./certifier/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist certifier

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh", "pytest"]
CMD []

FROM base AS production

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main

# add source and necessary files
COPY ./certifier/src/ ./src/
COPY ./certifier/LICENSE ./certifier/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist certifier

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh", "certifier"]
CMD []
