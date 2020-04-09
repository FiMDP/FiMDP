from setuptools import setup

setup(
    name='cdmp',
    version='1.0.1',
    keywords='polynomial-time, buchi-objective, agent, cmdp, controller-synthesis, formal-methods',
    url='https://github.com/pthangeda/consumption-MDP',
    description='Package with tools for Consumption Markov Decision Processes',
    packages=['cmdp'],
    install_requires=[
        'numpy>=1.18.1',
        'ipython>=7.13.0',
        'networkx>=2.4',
        'matplotlib>=3.2.1',
        'jupyter>=1.0.0'
    ]
)

