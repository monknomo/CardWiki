Setup for Cardwiki
==================

Use a virtual environment
--------------------------

### Linux/OSX users

```
pyenv virtualenv 3.3.4 create cardwiki
pyenv virtualenv activate cardwiki
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
```

### Windows Users

```
pywe --venv create cardwiki
pywe --venv activate cardwiki
```
    
Install required bcrypt libraries.  I find this a combo of annoying and difficult on Windows

Get Dependencies
------------------

### Everyone

```
pip install -r requirements.txt
python init_db.py
python run_cardwiki.py
```

Start Wikiing
---------------

Visit http://localhost:8080 to get started.  I'll write more documentation about how to use the wiki, but for now, init_db creates an explanatory wiki page that should be the first thing you see
