# when running this from a new virtual environment you run just bootstrap
# which will install the items needed for just lint
# I don't include these in the requirements.in kind of just because
@bootstrap:
    pip install black flake8 isort

@lint:
    black build-readme.py
    flake8 build-readme.py --ignore=E501
    isort build-readme.py

@install:
    pip-compile --generate-hashes
    pip install -r requirements.txt
