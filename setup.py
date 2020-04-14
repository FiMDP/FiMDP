from setuptools import setup

setup(
    name='fimdp',
    version='1.0.1',
    keywords='polynomial-time, buchi-objective, agent, cmdp, controller-synthesis, formal-methods',
    url='https://github.com/xblahoud/FiMDP',
    description='Package with tools for Resource-constrained Markov Decision Processes',
    packages=['fimdp'],
    install_requires=[
        'ipython>=7.13.0',
    ]
)

