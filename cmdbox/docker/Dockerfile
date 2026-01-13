#{FROM}

ARG MKUSER

#{COPY_CMDBOX}

RUN groupadd ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER} && \
    cp /etc/skel/.bash_logout /home/${MKUSER}/ && \
    cp /etc/skel/.bashrc /home/${MKUSER}/ && \
    cp /etc/skel/.profile /home/${MKUSER}/
RUN chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git wget
#{INSTALL_PYTHON}
RUN apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential libopencv-dev && \
    apt-get install -y iputils-ping net-tools
RUN pip install --upgrade pip && \
    pip install 'xmlsec==1.3.13' python3-saml && \
    pip install "pydantic>=2.0.0,<3.0.0" && \
    pip install 'fastmcp>=2.14.0' 'mcp>=1.10.0,<2.0.0' && \
    pip install 'google-adk>=1.21.0' litellm && \
    pip install 'a2a-sdk>=0.3.4,<0.4.0' && \
    pip install backoff cryptography orjson apscheduler litellm-enterprise email-validator fastapi-sso && \
    pip install #{INSTALL_CMDBOX} && cmdbox --version

#{INSTALL_VOICEVOX}
RUN pip install rich==14.2.0
RUN mkdir -p /home/${MKUSER}/.cmdbox && chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}/.cmdbox

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server#{INSTALL_TAG}
ENV MKUSER=${MKUSER}
ENV LISTEN_PORT=8081
ENV MCPSV_LISTEN_PORT=8082
ENV SVCOUNT=${SVCOUNT}

WORKDIR /home/${MKUSER}/
#{COPY_CMDBOX_START}
CMD bash
