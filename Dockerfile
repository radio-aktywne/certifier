ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG AS base

# add bash, because it's not available by default on alpine
RUN apk add --no-cache bash

# install poetry
COPY ./requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

# create new environment
# see: https://jcristharif.com/conda-docker-tips.html
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "certifier", "/bin/bash", "-c"]

# add poetry files
COPY ./certifier/pyproject.toml ./certifier/poetry.lock /tmp/certifier/
WORKDIR /tmp/certifier

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "certifier"]

FROM base AS test

# install dependencies only (notice that no source code is present yet) and delete cache
RUN poetry install --no-root --extras test && \
    rm -rf ~/.cache/pypoetry

# add source, tests and necessary files
COPY ./certifier/src/ /tmp/certifier/src/
COPY ./certifier/tests/ /tmp/certifier/tests/
COPY ./certifier/LICENSE ./certifier/README.md /tmp/certifier/

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist certifier

CMD ["pytest"]

FROM base AS production

# install dependencies only (notice that no source code is present yet) and delete cache
RUN poetry install --no-root && \
    rm -rf ~/.cache/pypoetry

# add source and necessary files
COPY ./certifier/src/ /tmp/certifier/src/
COPY ./certifier/LICENSE ./certifier/README.md /tmp/certifier/

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist certifier

CMD ["certifier"]
