#!/bin/bash

python3 test_buchi.py
python3 test_mecs.py
python3 test_reachability.py
python3 test_safety.py
python3 test_strategy.py
jupytext ../tutorials/StrategyTypes.py --to=ipynb
jupyter nbconvert --execute ../tutorials/StrategyTypes.ipynb 

