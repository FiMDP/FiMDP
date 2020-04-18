# FiMDP (Fuel in MDP)
## Artifact submitted to [CAV2020] together with the paper _Qualitative Controller Synthesis for Consumption Markov Decision Processes_

This docker image contains this file, a copy of the [accepted paper](cav2020_paper233.pdf), and three directories that are part of the software package called [FiMDP] (Fuel in MDP). FiMDP was used to perform the evaluation of the techniques presented in the paper. The directory [fimdp](fimdp) contains the implementation of the presented algorithms, [doc](doc) contains a local copy of documentation, and finally the directory [examples](examples) contains several [Jupyter] notebooks that work with FiMDP. The notebook [artifact_evaluation](artifact_evaluation.ipynb) is a guide to reproducing the results from our paper.

This docker is build automatically from `cav2020` branch of the GitHub repository of [FiMDP]. You can access the same code and notebooks online from your browser directly using [Binder] at this [link](https://mybinder.org/v2/gh/xblahoud/FiMDP/cav2020). The documentation for FiMDP can be also viewed online at [readthedocs].

1) To access the directory with the paper, FiMDP package, example notebooks directory, docs, and README, open a CLI and run:
   
```sh
sudo docker run -it xblahoud/fimdp:cav2020 /bin/bash
```

2) To access the Jupyter notebooks, open a CLI and run:
    
```sh
sudo docker run -p 8888:8888 xblahoud/fimdp:cav2020
```
    
    and then access the following link in your browser:
    
```sh
http://localhost:8888/tree/examples
```

3) The **artifact_evaluation.ipynb** notebook includes all the routines needed for reproducing 
the results reported in the paper. Additional details are provided in the notebook.

4) For detailed documentation and additional modes to access the package, visit the following
[link] or access it locally in the “/home/cav2020/docs/build/html” directory
by viewing the "index.html" file. You can read this file in your local browser via the Jupyter environment using:
    ```
    http://localhost:8888/view/docs/build/html/index.html
    ```

[CAV2020]: http://i-cav.org/2020/
[FiMDP]: https://github.com/xblahoud/FiMDP
[readthedocs.org]: https://fimdp.readthedocs.io/en/latest/
[Jupyter]: https://jupyter.org
[Binder]: https://mybinder.org