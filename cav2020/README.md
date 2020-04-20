# FiMDP (Fuel in MDP)
## Artifact submitted to [CAV2020] together with the paper _Qualitative Controller Synthesis for Consumption Markov Decision Processes_

This docker image contains this file, a copy of the [accepted paper](cav2020_paper233.pdf), and three directories that are part of the software package called [FiMDP] (Fuel in MDP). FiMDP was used to perform the evaluation of the techniques presented in the paper. The directory [fimdp](fimdp) contains the implementation of the presented algorithms, [doc](doc) contains offline documentation, and finally, the directory [examples](examples) contains several [Jupyter] notebooks that work with FiMDP. The notebook [artifact_evaluation](artifact_evaluation.ipynb) is a guide to reproducing the results from our paper.

This docker is build automatically from the `cav2020` branch of the GitHub repository of [FiMDP]. You can access the same code and notebooks online from your browser directly using [Binder] at https://mybinder.org/v2/gh/xblahoud/FiMDP/cav2020. The documentation for FiMDP can also be viewed online at [readthedocs].

### Using the docker image
The default behavior of this image is to run Jupyter lab, and that is also the intended usage. To open the Jupyter lab environment in your browser, you need the following two steps.

1. **Launch the Jupyter lab server** inside a docker container for this image.  Note that the `-p 7777:8888` redirects the port 8888 of the container to the port 7777 of your computer. If the latter is already used on your computer, use another number.

```sh
sudo docker run --rm=true -p 7777:8888 xblahoud/fimdp:cav2020
```

NOTE: Using the `--rm=true` option causes Docker to cleanup the container instance on exit, meaning that any files you create in the container will be lost. If you do not use this option (the default is `--rm=false`) you can restart a previously exited container with `sudo docker start -a b5d1c544c0df`. The container's name (in this example `b5d1c544c0df`) is displayed in the prompt of the shell, but can also be found with `sudo docker ps -a`.

2. **Connect to the server** from your local browser. Just go to http://localhost:7777/lab in your browser.


To display this file in your browser, right-click on the README.md file in the left panel and select _open with > Markdown preview_.

If you prefer the classic Jupyter notebook environment to Jupyter lab, type `tree` instead of `lab`.

### Reproducing results from the paper
The fastest way to reproduce the results is to run the [artifact_evaluation](examples/artifact_evaluation.ipynb) notebook in the [examples](examples) directory. It includes all the routines needed for reproducing the results reported in the paper. Additional details are provided in the notebook. We also recommend to read the documentation for the examples (see below) or the simplified version in [examples/README.md](examples/README.md) (you can again render it using right-click on the file and selecting _open with > Markdown preview_). The documentation gives more details about the models used for this evaluation.

#### Accessing the offline documentation of FiMDP
After the jupyter server is started, you can use it to render the documentation from docker in your browser. Just go to http://localhost:7777/view/docs/build/html/index.html. We recommend reading the section examples that discuss all the attached notebooks and considered case studies.

### Terminal access
In order to explore this image from a terminal, run the following:

```sh
sudo docker run -it xblahoud/fimdp:cav2020 /bin/bash
```

[CAV2020]: http://i-cav.org/2020/
[FiMDP]: https://github.com/xblahoud/FiMDP
[readthedocs.org]: https://fimdp.readthedocs.io/en/latest/
[Jupyter]: https://jupyter.org
[Binder]: https://mybinder.org