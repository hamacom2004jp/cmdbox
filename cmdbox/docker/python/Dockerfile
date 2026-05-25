FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        wget \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install cmdbox

RUN groupadd -f sandbox && \
    useradd -m -g sandbox -s /bin/bash sandbox

RUN mkdir -p /sandbox && chown sandbox:sandbox /sandbox

USER sandbox
WORKDIR /sandbox

CMD ["python3"]
