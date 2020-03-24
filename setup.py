from setuptools import setup

setup(
    name='pacscdmp',
    version='1.0.1',
    keywords='polynomial-time, buchi-objective, agent, cmdp, controller-synthesis, formal-methods',
    url='https://github.com/pthangeda/consumption-MDP',
    description='Polynomial-time Algorithm for Controller Synthesis in Consumption Markov Decision Processes',
    packages=['pacscmdp'],
    install_requires=[
        'numpy>=1.15.0',
        'ipython>=7.6',
        'networkx>=2.4',
        'folium>=0.10.1'
    ]
)