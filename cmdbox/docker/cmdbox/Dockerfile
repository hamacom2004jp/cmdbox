#{FROM}
#{INIT_EXTRA}
ARG MKUSER
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
RUN apt-get update && \
    apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential libopencv-dev && \
    apt-get install -y iputils-ping net-tools && \
    apt-get install -y ffmpeg
#{INSTALL_TORCH}
RUN pip install --upgrade pip && \
    pip install "pydantic>=2.0.0,<3.0.0" "fastmcp>=2.14.4" "mcp>=1.23.0,<2.0.0" && \
    pip install "google-adk>=1.23.0" "a2a-sdk>=0.3.4,<0.4.0" "litellm>=1.75.5,<1.80.17" && \
    pip install "sentence-transformers" "sqlite_vec" "transformers>=4.48.0" && \
    pip install "chunklet-py[document]" "langchain_community" "markdown" "pdfplumber" && \
    pip install "accelerate>=1.12.0" "qwen-omni-utils>=0.0.9"
#{RUN_EXTRA_PRE}
#{COPY_CMDBOX}
RUN pip install #{INSTALL_CMDBOX} && cmdbox --version
#{INSTALL_EXTRA}
#{RUN_EXTRA_POST}
#{INSTALL_VOICEVOX}
RUN pip install rich==14.2.0
#{MK_DATA_DIR}
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=password
ENV SVNAME=server#{INSTALL_TAG}
ENV MKUSER=${MKUSER}
ENV LISTEN_PORT=8081
ENV SSL_LISTEN_PORT=8443
ENV MCPSV_LISTEN_PORT=8091
ENV SSL_MCPSV_LISTEN_PORT=8453
ENV A2ASV_LISTEN_PORT=8071
ENV SSL_A2ASV_LISTEN_PORT=8433
ENV LANGUAGE=${LANGUAGE}
ENV SVCOUNT=${SVCOUNT}
#{ENV_EXTRA}
WORKDIR /home/${MKUSER}/
#{COPY_CMDBOX_START}
CMD bash