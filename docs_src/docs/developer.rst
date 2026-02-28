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
        python -m build

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

Reference: Procedure for Setting Up a WSL2-Ubuntu 24.04-Docker Environment
================================================================================

1. Installing WSL2

    Execute the following command in the Windows Command Prompt:

    .. code-block:: bat

        wsl --install -d Ubuntu-24.04

    Set the ID and password for `ubuntu`, and then start Ubuntu.

2. Initial Ubuntu Setup

    Log in to the launched Ubuntu and execute the following commands:

    .. code-block:: bash

        cd /etc/apt
        sudo apt-get update && sudo apt-get install -y language-pack-ja
        sudo update-locale LANG=ja_JP.UTF-8
        sudo apt-get install -y manpages-ja manpages-ja-dev python3.12-dev python3.12-venv libopencv-dev
        sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

3. Installing Docker

    Execute the following commands in the same Ubuntu environment:

    .. code-block:: bash

        sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io && docker --version
        sudo apt-get install -y docker-compose-plugin && docker compose version
        sudo systemctl start docker && sudo systemctl enable docker
        sudo usermod -aG docker $USER
        newgrp docker

    If you want to use a GPU, execute the following commands as well:

    .. code-block:: bash

        cd ~
        wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
        sudo dpkg -i cuda-keyring_1.1-1_all.deb
        sudo apt-get update
        sudo apt-get -y install cuda-toolkit-13-1

        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
          && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        sudo apt-get update
        sudo apt-get install -y nvidia-container-toolkit
        nvidia-container-toolkit info

4. Creating a WSL-Ubuntu-cuda_docker file

    Execute the following command in the Windows Command Prompt:

    .. code-block:: bat

        wsl --shutdown
        wsl --export Ubuntu-24.04 <AnyPath>/Ubuntu_cuda_docker-24.04.tar
        wsl --unregister Ubuntu-24.04
        wsl --import Ubuntu_cuda_docker-24.04 <AnyPath>/Ubuntu_cuda_docker-24.04 <AnyPath>/Ubuntu_cuda_docker-24.04.tar --version 2

5. Starting WSL-Ubuntu-cuda_docker

    Execute the following command in the Windows Command Prompt:

    .. code-block:: bat

        cd <AnyPath>
        wsl -d Ubuntu_cuda_docker-24.04 -u ubuntu

6. WSL Image Compaction

    Execute the following command in the Windows Command Prompt:

    .. code-block:: bat

        diskpart
        diskpart > select vdisk file="<AnyPath>\ext4.vhdx"
        diskpart > attach vdisk readonly
        diskpart > compact vdisk
        diskpart > detach vdisk
        diskpart > exit

Reference: How to Use USB Devices in a WSL Environment
==============================================================

- To use USB devices in Ubuntu on WSL2, follow these steps: `Original Article <https://learn.microsoft.com/ja-jp/windows/wsl/connect-usb>`__

    1. Install USBIPD on WSL. `Download Site <https://github.com/dorssel/usbipd-win/releases>`__
    2. Open a command prompt in administrator mode and execute the following command.

        .. code-block:: bat

            usbipd list

    3. Note the BUSID of the device you want to attach.
    4. Share the device using the following command. (If the BUSID is '3-1')

        .. code-block:: bat

            usbipd bind --busid 3-1

    5. Attach the device to WSL using the following command. (If the BUSID is '3-1')

        .. code-block:: bat

            usbipd attach --wsl --busid 3-1

    6. Verify that the USB device is available in Ubuntu on WSL.

        .. code-block:: sh

            lsusb

