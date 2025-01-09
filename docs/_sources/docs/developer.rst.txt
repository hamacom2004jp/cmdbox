.. -*- coding: utf-8 -*-

********************************
Developer Information
********************************

This section describes the steps to build a development environment for cmdbox.

How to install the project
==============================

To install the project, follow these steps:

1. Clone project:

    .. code-block:: bash

        git clone https://github.com/hamacom2004jp/cmdbox.git

2. Go to the project directory:

    .. code-block:: bash

        cd cmdbox

3. Create a virtual environment for your project:

    .. code-block:: bash

        python -m venv .venv
        . .venv/bin/activate

4. Install project dependencies:

    .. code-block:: bash

        python.exe -m pip install --upgrade pip
        pip install -r requirements.txt

5. Build the project:

    .. code-block:: bash

        sphinx-apidoc -F -o docs_src/resources cmdbox
        sphinx-build -b html docs_src docs
        python -m collectlicense --out cmdbox/licenses --clear
        python setup.py sdist
        python setup.py bdist_wheel

.. sphinx-build -b gettext docs_src docs_build
.. sphinx-intl update -p docs_build -l en

How to commit a module
=========================

If you are willing to cooperate in the development, please follow these guidelines:

1. Create a new branch:

    .. code-block:: bat

        git checkout -b feature/your-feature

2. Make your changes and commit!:

    .. code-block:: bat

        git commit -m "Add your changes"

3. Push to the branch you created:

    .. code-block:: bat

        git push origin feature/your-feature

4. Create a pull request.


Reference: Procedure for building a Windows environment for Redis
====================================================================

- `cmdbox` uses Redis.

    1. Download the installer from `GitHub <https://github.com/MicrosoftArchive/redis/releases>`__ .
    2. Run the downloaded installer (MSI file).
    3. The wizard will ask you to set the installation directory, so please make a note of the path you set. The default is `C:\\Program Files\\Redis` .
    4. In the wizard, there is a setting for the service port of the Redis server, so please make a note of the port you set. The default is 6379.
    5. There is a setting in the wizard for the maximum amount of memory to be used, so set it as needed. For development use, about 100 mb is sufficient. 
    6. After installation is complete, open the installation directory in Explorer.
    7. Open the `redis.windows-service.conf` and `redis.windows-service.conf` files in it with a text editor such as Notepad.
    8. In this file, search for `requirepass foobared`, remove the `#` and uncomment it out.
    9. Change the `foobared` part of `requirepass foobared` to your desired password. Make a note of the changed password.
    10. This password will be the password specified in the `cmdbox` command.
    11. Open the Windows Task Manager, open the Services tab, right-click `Redis`, and restart the service.
