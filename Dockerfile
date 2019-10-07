FROM python:3-alpine
LABEL maintainer="Rodrigo Cristiano - rcristianofv@hotmail.com.br"
LABEL Version="1.0"

COPY . /code
WORKDIR /code
RUN set -e && \
    apk add git && \
    pip install -r requirements.txt && \
    pip install --editable . && \
    rm -Rf *
