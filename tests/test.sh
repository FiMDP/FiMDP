#!/bin/bash
set -e

python3 test_buchi.py
python3 test_storm_io.py
python3 test_lcmdp.py
python3 test_mecs.py
python3 test_mincap.py
python3 test_product.py
python3 test_product_selector.py
python3 test_reachability.py
python3 test_safety.py
python3 test_strategy.py
python3 test_strategy_old.py
jupyter nbconvert --execute ../tut/ExplicitEnergy.ipynb --to html
jupyter nbconvert --execute ../tut/Labeled.ipynb --to html
jupyter nbconvert --execute ../tut/Solvers.ipynb --to html
jupyter nbconvert --execute ../tut/StormAndPrism.ipynb --to html
