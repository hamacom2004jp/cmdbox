.. -*- coding: utf-8 -*-

**************
Install
**************

- Install cmdbox with the following command.
- Also install the docker version of the redis server.

.. code-block:: bash

    docker run -p 6379:6379 --name redis -e REDIS_PASSWORD=password -it ubuntu/redis:latest
    pip install cmdbox
    cmdbox -v

- When using SAML in web mode, install the modules with dependencies.

.. code-block:: bash

    pip install xmlsec==1.3.13 python3-saml
    apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential libopencv-dev

- When using `--agent use` in web mode, install the modules with dependencies.

.. code-block:: bash

    pip install google-adk litellm

