FROM python:3.12

WORKDIR /opt/plugfs

# Install Poetry
RUN set eux; \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python; \
    cd /usr/local/bin; \
    ln -s /opt/poetry/bin/poetry; \
    poetry config virtualenvs.create false; \
    poetry self add poetry-plugin-sort

COPY ./pyproject.toml ./poetry.lock /opt/plugfs/

RUN poetry install --no-root

COPY . /opt/plugfs
ENV PYTHONPATH=/opt/plugfs
