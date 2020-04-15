# Instructions for Artifact Evaluation

The scripts for reproducing the results reported in the paper are organized 
in Jupyter notebooks packaged into a docker image. To reproduce the results and
to explore our tool, use the following steps:

Note: If you are already in the docker image root or running notebooks in Binder, skip to step 4.

1) Install docker (https://docs.docker.com/get-docker) - requires root access. 
    -> Alternative to docker is using Binder to running the notebooks in a web browser.
       Click on the following link https://mybinder.org/v2/gh/xblahoud/FiMDP/master and follow
       skip to step 4.
    
2) To access the directory with the paper, FiMDP package, example notebooks directory, docs, and README, open a CLI and run:
    -> sudo docker run -it xblahoud/fimdp:cav2020 /bin/bash

3) To access the Jupyter notebooks, open a CLI and run:
    -> sudo docker run -p 8888:8888 xblahoud/fimdp:cav2020

    and then access the following link in your browser:
    -> http://localhost:8888/tree/examples

4) The 'artifact_evaluation.ipynb' notebook includes all the routines needed for reproducing 
the results reported in the paper. Additional details are provided in the notebook.

5) For detailed documentation and additional modes to access the package, visit the following
link https://fimdp.readthedocs.io/en/latest/ or access it locally in the “/home/cav2020/docs/html” directory
by viewing the "index.html" file.
