from fabric.api import run, cd, env, settings, hosts 
from fabric.contrib.files import exists

#change this to something sensible
env.hosts =['localhost']
env.user = 'cardwiki'
env.password = 'default'

def diagnose():
	print(env.shell)
	run("source .bashrc && echo $PATH")
	with settings(warn_only=True):
		if run("command -v pyenv > /dev/null 2>&1").failed:
			print("no pyenv")
		else:
			print("pyenv found")
	#run("which pyenv")
	run("ls")
	run("pwd")
	run("whoami")

def install_pyenv():
	install_required = False
	with settings(warn_only=True):
		if run("command -v pyenv > /dev/null 2>&1").failed:
			install_required = True
	if install_required:
		print("installing pyenv+pyenv-virtualenv")
		install_dir = '$HOME/pyenv'
		run("git clone https://github.com/yyuu/pyenv.git {0}".format(install_dir))
		#setup the path, etc
		run("echo 'export PYENV_ROOT={0}' >> $HOME/.bash_profile".format(install_dir))
		run("echo 'export PATH=\"$PYENV_ROOT/bin:$PATH\"' >> $HOME/.bash_profile")
		run("echo 'eval \"$(pyenv init -)\"' >> $HOME/.bash_profile")				
		run("git clone https://github.com/yyuu/pyenv-virtualenv.git {0}/plugins/pyenv-virtualenv".format(install_dir))
		run("echo 'eval \"$(pyenv virtualenv-init -)\"' >> $HOME/.bash_profile")
		run("exec $SHELL")
		print("pyenv+pyenv-virtualenv installed")
	else:
		print("pyenv install detected")

def prepare_virtualenv():
	virtualenv_name = 'cardwiki0'
	python_version = "3.4.2"
	with settings(warn_only=True):
		if run("pyenv local {0}".format(python_version)).failed:
			install_pyenv()
			run("pyenv install {0}".format(python_version))
	run("pyenv local {0}".format(python_version))
	with settings(warn_only=True):
		if run("pyenv activate {0}".format(virtualenv_name)).failed:
			run("pyenv virtualenv {0} {1}".format(python_version, virtualenv_name))
	#pyenv activate {0}.format(virtualenv_name)
	run("pyenv activate {0} && pip install bottle".format(virtualenv_name))
	run("pyenv activate {0} && pip install sqlalchemy".format(virtualenv_name))
	run("pyenv activate {0} && pip install markdown".format(virtualenv_name))

def prepare_code():
	code_dir = '$HOME/CardWiki'
	virtualenv_name = 'cardwiki0'
	prepare_virtualenv()
	#if not exists(code_dir):
	#	run("mkdir {0}".format(code_dir))
	if not exists("./CardWiki"):
		run("git clone https://github.com/monknomo/CardWiki.git".format(code_dir))
	with cd(code_dir):
		run("pyenv activate {0} && python init.py".format(virtualenv_name))
	
def prepare_webserver():
	virtualenv_name = 'cardwiki0'
	run("pyenv activate {0} && pip install gunicorn".format(virtualenv_name))
	#code_dir = '$HOME/aiohttp'
	#virtualenv_name = 'cardwiki0'
	#if not exists("{0}".format(code_dir)):
	#	run("git clone https://github.com/KeepSafe/aiohttp.git")
	#with cd(code_dir):
	#	run("pyenv activate {0} && python setup.py install".format(virtualenv_name))

def prepare():
	prepare_virtualenv()
	prepare_code()
	prepare_webserver()
	
def stop_server():
	server_dir = '$HOME'
	stop_server = False
	with settings(warn_only=True):
		if not run("test -e {0}/gunicorn.pid".format(server_dir)).failed:
			stop_server = True			
	if stop_server:
		run("cat $HOME/gunicorn.pid")
		run("kill $(cat {0}/gunicorn.pid) && rm {0}/gunicorn.pid".format(server_dir))
	else:
		print("gunicorn pid missing, a human will have to take this")
						
def start_server():
	server_dir = '$HOME'
	start_server = False
	with settings(warn_only=True):
		if run("test -e {0}/gunicorn.pid".format(server_dir)).failed:
			start_server = True
	if start_server:
		with cd('$HOME/CardWiki'):
			run("pyenv activate cardwiki0 && gunicorn -D --pid $HOME/gunicorn.pid --access-logfile $HOME/access.log --error-logfile $HOME/error.log -w 4 -b 127.0.0.1:18383 run_cardwiki:app")
	else:
		print("gunicorn pid present, the server might be running?")

def restart_server():
	stop_server()
	start_server()

def deploy():
	code_dir = '$HOME/CardWiki'
	stop_server()
	with settings(warn_only=True):
		if run("test -d {0}".format(code_dir)).failed:
			run("git clone https://github.com/monknomo/CardWiki.git {0}".format(code_dir))
	with cd(code_dir):
		run("git fetch --all")
        run("git reset --hard origin/master")
	start_server()		
	

