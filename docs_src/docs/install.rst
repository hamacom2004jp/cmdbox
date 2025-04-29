.. -*- coding: utf-8 -*-

**************
Install
**************

- Install cmdbox with the following command.

.. code-block:: bash

    pip install cmdbox
    cmdbox -v

- When using SAML in web mode, install the modules with dependencies.

.. code-block:: bash

    pip install xmlsec==1.3.13 python3-saml
    apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential libopencv-dev

- Also install the docker version of the redis server.

.. code-block:: bash

    docker run -p 6379:6379 --name redis -it ubuntu/redis:latest
