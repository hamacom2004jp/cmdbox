.. -*- coding: utf-8 -*-

**************
Install
**************

- Install cmdbox with the following command.

.. code-block:: bash

    pip install cmdbox
    cmdbox -v

- Also install the docker version of the redis server.

.. code-block:: bash

    docker run -p 6379:6379 --name redis -it ubuntu/redis:latest
