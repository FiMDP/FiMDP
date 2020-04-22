.. _install:

Installation and Usage
=======================

This section details the installation and usage steps for multiple modes of accessing the tool and the examples.
FiMDP requires Python 3.7 or above. The dependency on external packages is minimal and they are mainly used for 
illustrations. The examples presented in interactive Jupyter notebooks help in getting started with the tool and also 
to analyze the performance for provided examples.

Binder
-------
`Binder <https://mybinder.org/>`_ creates custom computing environments from git repositories and deploys on the 
cloud allowing access to interactive notebooks over any web browser. Use the following steps to get started with Binder:

- Click on the following `link <https://mybinder.org/v2/gh/xblahoud/FiMDP/master/>`_ and wait for the environment to load.
- once the cloud instance of Jupyter notebook begins, navigate to the `examples` directory and access any notebook of interest.
- For detailed description of all the example notebooks, please visit the examples section :ref:`examples`.

.. note:: Large jobs might take significant computation time on Binder as the performance is usually lower than a modern local workstation. 

Docker
-------
The docker image with FiMDP is published on `Docker Hub <https://hub.docker.com/repository/docker/xblahoud/fimdp>`_. 
To access the package using docker, download and install `docker <https://docs.docker.com/get-docker/>`_ on your machine.
The default behavior of this image is to run Jupyter lab, and that is also the intended usage. 
To open the Jupyter lab environment in your browser, you need the following two steps.

Access the Jupyter notebooks
*****************************

To open the interactive Jupyter notebooks with examples via Jupyter lab, open a CLI and run:
::

    sudo docker run --rm=true -p 7777:8888 xblahoud/fimdp:cav2020

Note that the `-p 7777:8888` redirects the port 8888 of the container to the port 7777 of your computer. 
If the latter is already used on your computer, use another number. After running the above command, access the following url 
in a browser in your machine:
::

    http://localhost:7777/lab


To get started, right-click on the README.md file in the left panel and select *open with > Markdown preview*. If you prefer 
the classic Jupyter notebook environment to Jupyter lab, type `tree` instead of `lab`.

Run bash in this container
**************************

Open a CLI and run:
::

    sudo docker run -it xblahoud/fimdp:cav2020 /bin/bash


and the directory contains the all the source files of the package.

Conda Installation
--------------------
We assume that you are familiar with the `Anaconda <https://www.anaconda.com/>`_ eco-system and the `conda <https://docs.conda.io/en/latest/>`_ environment and 
have an active installation of Anaconda or Miniconda on your computer. To use our tool with the help of conda:

- Create a new conda environment with the name `fimdp` using the following command::

    conda create -n fimdp python=3.7

- Clone our `GitHub repository <https://github.com/xblahoud/FiMDP>`_ and install the required packages in the newly created environment using the following command::

    conda install --name fimdp -c conda-forge --file requirements.txt

- Activate the environment using the following command::

    conda activate fimdp

- Launch Jupyter notebook server using the following command::
    
    jupyter notebook

- Navigate local instance of Jupyter to access the examples subdirectory and access the notebooks.

Certain examples include visualizations that need the `GraphViz <https://www.graphviz.org/>`_ package installed and configured. Download and install the appropriate version
of the package and add the `dot` file to the system PATH to successfully run certain examples. If you install `GraphViz` package using Anaconda, make sure that to add the PATH
of the `dot` file from Anaconda library to your system PATH. 

Pip Installation
-----------------
We assume that you have the default Python environment already configured on your computer and you intend to use our tool inside of it. 
If you want to create and work with Python virtual environments, please follow instructions on `virtual environments <https://docs.python.org/3/library/venv.html>`_.

To get the latest version of FiMDP, you can clone the `GitHub repository <https://github.com/xblahoud/FiMDP>`_ and install the dependencies with `pip3`:
::

    git clone https://github.com/xblahoud/FiMDP
    cd FiMDP
    pip3 install -e .
    
Further, certain examples include visualizations that need the `GraphViz <https://www.graphviz.org/>`_ package installed and configured. Download and install the appropriate version
of the package and add the `dot` file to the system PATH to successfully run certain examples.

After the installation, you can start a local instance of Jupyter notebook and access the examples. 




