from __future__ import with_statement
from fabric.api import *
import os
import fabric.contrib.project as project

#GIT_BRANCH = local("git branch | grep '^*' | cut -d' ' -f2", capture=True)
GIT_BRANCH = local('git rev-parse --abbrev-ref HEAD', capture=True)

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEPLOY_FOLDER = None
DEPLOY_PATH = None

def _init():
    global HYDE_CONFIG
    HYDE_CONFIG = 'site-{}.yaml'.format(DEPLOY_TYPE)
    global DEPLOY_FOLDER
    DEPLOY_FOLDER = 'deploy-{}-{}.albertdelafuente.com'.format(GIT_BRANCH, DEPLOY_TYPE)
    global DEPLOY_PATH
    DEPLOY_PATH = os.path.join(ROOT_PATH, '..', DEPLOY_FOLDER)

def _hyde(args):
    return local('hyde -x {}'.format(args))

def _clean():
    _init()
    local('rm -rf {}'.format(DEPLOY_PATH))
    local('rm -rf content/blog/tags')

def _deploy():
    _init()
    _clean()
    if DEPLOY_TYPE == 'local':
        local('ln -sf ~/Dropbox/appdata/hydesite/private ./content')
    else:
        #local('find content/ -maxdepth 1 -type l -delete')
        local('rm -f content/private')
    _hyde('gen -c {} -d {}'.format(HYDE_CONFIG, DEPLOY_PATH))

def _run():
    _deploy()
    local('cd {} && python -m SimpleHTTPServer'.format(DEPLOY_PATH))

@task
def clean_web():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'web'
    _clean()

@task
def clean_develop():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'develop'
    _clean()

@task
def clean_local():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'local'
    _clean()

@task
def deploy_web():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'web'
    _deploy()

@task
def deploy_develop():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'develop'
    _deploy()

@task
def deploy_local():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'local'
    _deploy()

@task
def run_web():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'web'
    _run()

@task
def run_develop():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'develop'
    _run()

@task
def run_local():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'local'
    _run()

@task
def clean():
    clean_web()

@task
def clean_all():
    clean_web()
    clean_develop()
    clean_local()

@task
def deploy():
    deploy_web()

@task(default=True)
def run():
    run_web()

def _hidden_run(cmd):
    with hide('output','running','warnings'), settings(warn_only=True):
        return local(cmd)

@task
def test_web_compile():
    deploy_web()
    GH_CNAME = os.getenv('GH_CNAME')
    GH_USER_EMAIL = os.getenv('GH_USER_EMAIL')
    GH_USER_NAME  = os.getenv('GH_USER_NAME')
    TRAVIS_BUILD_NUMBER  = os.getenv('TRAVIS_BUILD_NUMBER')
    GH_TOKEN = os.getenv('GH_TOKEN')
    GH_USER_LOGIN = os.getenv('GH_USER_LOGIN')
    GH_PUSH_REPO  = os.getenv('GH_PUSH_REPO')
    local('cd {}'.format(DEPLOY_PATH))
    local('touch .nojekyll')
    local('echo "{}" > CNAME'.format(GH_CNAME))
    local('git init')
    local('git config user.email "{}"'.format(GH_USER_EMAIL))
    local('git config user.name "{}"'.format(GH_USER_NAME))
    local('git add -A .')
    local('git commit -a -m "Travis #{}"'.format(TRAVIS_BUILD_NUMBER))
    _hidden_run('git remote add origin https://{}@github.com/{}/{}'.format(
        GH_TOKEN,
        GH_USER_LOGIN,
        GH_PUSH_REPO))
    _hiden_run('git push --quiet --force origin master > /dev/null 2>&1')

def smush():
    local('smusher ./media/images')

#@hosts(PROD)
#def publish():
#    regen()
#    project.rsync_project(
#        remote_dir=DEST_PATH,
#        local_dir=DEPLOY_PATH.rstrip('/') + '/',
#        delete=True
#    )
