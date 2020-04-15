FROM continuumio/miniconda3
LABEL url="https://github.com/xblahoud/FiMDP"

COPY requirements-dev.txt /tmp/

# configure conda and install packages
RUN conda config --set show_channel_urls true && \
	conda config --set channel_priority strict && \
    conda config --prepend channels conda-forge && \
    conda update --yes -n base conda && \
    conda install --update-all --force-reinstall --yes --file /tmp/requirements.txt && \
    conda clean --all --yes && \
    conda info --all && \
    conda list

# launch jupyter in the local working directory that we mount
WORKDIR /home/cav2020

COPY examples/ ./examples
COPY fimdp/ ./fimdp
COPY cav2020/ .

# build docs and copy files
COPY docs/ ./docs
RUN cd docs && make html

# set default command to launch when container is run
CMD ["jupyter", "notebook", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
