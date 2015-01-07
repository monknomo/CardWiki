from fabric.api import run, cd, env, settings, hosts, 

#change this to something sensible
env.hosts = ['localhost']

def install_pyenv():
	with settings(warn_only=True):
		if run("command -v pyenv >/dev/null 2>&1").failed:
			with settings(warn_only=True):
				print("installing pyenv+pyenv-virtualenv")
				install_dir = '/opt/pyenv'
				run("git clone https://github.com/yyuu/pyenv.git {0}".format(install_dir))
				#setup the path, etc
				run("echo 'export PYENV_ROOT={0}' >> /etc/profile.d/pyenv.sh".format(install_dir))
				run("echo 'export PATH=\"$PYENV_ROOT/bin:$PATH\"' >> /etc/profile.d/pyenv.sh")
				run("echo 'eval\"$(pyenv init -)\"' >> /etc/profile.d/pyenv.sh")				
				run("git clone https://github.com/yyuu/pyenv-virtualenv.git {0}/plugins/pyenv-virtualenv".format(install_dir))
				run("echo 'eval\"$(pyenv virtualenv-init -)\"' >> /etc/profile.d/pyenv.sh")
				run("exec $SHELL")
				print("pyenv+pyenv-virtualenv installed")
		else:
			print("pyenv install detected")

def prepare_virtualenv():
	virtualenv_name = 'cardwiki0'
	with settings(warn_only=True):
		if run("pyenv local 3.4").failed:
			install_pyenv()
			run("pyenv install 3.4")
	run("pyenv local 3.4")
	with settings(warn_only=True):
		if run("pyenv activate {0}".format(virtualenv_name)).failed:
			run("pyenv virtualenv {0}".format(virtualenv_name))
	run("pyenv activate {0}".format(virtualenv_name))
	run("pip install bottle")
	run("pip install sqlalchemy")
	run("pip install markdown")

def prepare_code():
	code_dir = '/opt/cardwiki'
	prepare_virtualenv()
	run("mkdir {0}".format(code_dir))
	run("git clone https://github.com/monknomo/CardWiki.git {0}".format(code_dir))
	cd(code_dir)
	run("python init.py")
	
def prepare_webserver():
	code_dir = '/opt/cardwiki'
	cd(code_dir)
	run("git clone https://github.com/KeepSafe/aiohttp.git")
	cd("aiohttp")
	run("python setup.py")

def prepare():
	code_dir = '/opt/cardwiki'
	prepare_virtualenv()
	prepare_code()
	prepare_webserver()
	
			
def deploy():
	code_dir = '/opt/cardwiki/'
	with settings(warn_only=True):
		if run("test -d {0}".format(code_dir)).failed:
			run("git clone https://github.com/monknomo/CardWiki.git {0}".format(code_dir))
	with cd(code_dir):
		run("git pull")
		
	

