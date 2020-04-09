from setuptools import setup

setup(
    name='cdmp',
    version='1.0.1',
    keywords='polynomial-time, buchi-objective, agent, cmdp, controller-synthesis, formal-methods',
    url='https://github.com/pthangeda/consumption-MDP',
    description='Package with tools for Consumption Markov Decision Processes',
    packages=['cmdp'],
    install_requires=[
        'ipython>=7.13.0',
    ]
)

