#{FROM}
#{INIT_EXTRA}
ARG MKUSER
RUN groupadd -f ${MKUSER} && \
    useradd -m -g ${MKUSER} -s /usr/bin/bash ${MKUSER} || true && \
    cp /etc/skel/.bash_logout /home/${MKUSER}/ && \
    cp /etc/skel/.bashrc /home/${MKUSER}/ && \
    cp /etc/skel/.profile /home/${MKUSER}/
RUN chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
RUN apt-get update && \
    apt-get install -y libgl1-mesa-dev libglib2.0-0 git wget
#{INSTALL_PYTHON}
RUN apt-get install -y python3-venv && python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN apt-get update && \
    apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential libopencv-dev && \
    apt-get install -y iputils-ping net-tools && \
    apt-get install -y ffmpeg
RUN pip install --upgrade pip
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