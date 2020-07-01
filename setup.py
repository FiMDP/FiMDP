from setuptools import setup
import pathlib

from fimdp import __version__ as version

# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='fimdp',
    version=version,
    description='Package with tools for Resource-constrained Markov Decision Processes',
    long_description=README,
    long_description_content_type="text/markdown",
    keywords='polynomial-time, buchi-objective, agent, cmdp, controller-synthesis, formal-methods',
    url='https://github.com/xblahoud/FiMDP',
    author="Fanda Blahoudek",
    author_email="fandikb+dev@gmail.com",
    license="MIT",
    python_requires=">=3.6.0",
    packages=['fimdp'],
    install_requires=[
        'ipython>=7.13.0',
    ]
)

