Setup for Cardwiki
==================

Use a virtual environment
--------------------------

### Linux/OSX users

pyenv virtualenv 3.3.4 create cardwiki
pyenv virtualenv activate cardwiki

### Windows Users

pywin --venv create cardwiki
pywin --venv activate cardwiki

Get Dependencies
------------------

### Everyone

pip install bottle
pip install markdown
pip install sqlalchemy
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
pip install bcrypt

python init.py

python run_cardwiki.py

Start Wikiing
---------------

visit http://localhost:8080 to get started
