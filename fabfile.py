from __future__ import with_statement
from fabric.api import *
import os

GIT_BRANCH = local('git rev-parse --abbrev-ref HEAD', capture=True)

PORT = 7653
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEPLOY_FOLDER = None
DEPLOY_PATH = None


def local_no_exception(command):
    try:
        local(command)
    except:
        pass


def _init():
    global HYDE_CONFIG
    HYDE_CONFIG = 'site-{}.yaml'.format(DEPLOY_TYPE)
    global DEPLOY_FOLDER
    DEPLOY_FOLDER = 'deploy'
    global DEPLOY_PATH
    DEPLOY_PATH = os.path.join(ROOT_PATH, DEPLOY_FOLDER)


def _hyde(args):
    return local('hyde -x {}'.format(args))


def _unlink_private():
    local('find content/en -maxdepth 1 -type l -delete')
    local('find content/en/blog -maxdepth 1 -type l -delete')


def _clean():
    _init()
    local('rm -rf {}'.format(DEPLOY_PATH))
    local('rm -rf content/blog/tags')
    _unlink_private()


@task
def kill():
    try:
        local('pkill -f "hyde -x serve"')
    except:
        pass


def _deploy():
    _init()
    _clean()
    if DEPLOY_TYPE == 'local':
        local_no_exception(
            'ln -s ~/Dropbox/appdata/hydesite/en/* ./content/en')
        local_no_exception(
            'ln -s ~/Dropbox/appdata/hydesite/en/blog/* ./content/en/blog/')
#        local_no_exception(
#            'ln -s ~/Dropbox/appdata/hydesite/pt/* ./content/pt')
#        local_no_exception(
#            'ln -s ~/Dropbox/appdata/hydesite/pt/blog/* ./content/pt/blog/')
    else:
        _unlink_private()
    _hyde('gen -c {} -d {}'.format(HYDE_CONFIG, DEPLOY_PATH))
    # Clean again not to stage files by error
    _unlink_private()


def _run():
    _deploy()
    kill()
    _hyde('serve -c {} -d {} -p {}'.format(HYDE_CONFIG, DEPLOY_PATH, PORT))


@task
def clean_web():
    global DEPLOY_TYPE
    DEPLOY_TYPE = 'web'
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
    clean_local()


@task
def deploy():
    deploy_web()


@task(default=True)
def run():
    run_web()


def _hidden_run(cmd):
    with hide('output', 'running', 'warnings'), settings(warn_only=True):
        return local(cmd)


def _travis_push_github(repo, branch, cname):
    GH_USER_EMAIL = os.getenv('GH_USER_EMAIL')
    GH_USER_NAME = os.getenv('GH_USER_NAME')
    TRAVIS_BUILD_NUMBER = os.getenv('TRAVIS_BUILD_NUMBER')
    GH_TOKEN = os.getenv('GH_TOKEN')
    GH_USER_LOGIN = os.getenv('GH_USER_LOGIN')
    with lcd(DEPLOY_PATH):
        local('touch .nojekyll')
        _hidden_run('echo "{}" > CNAME'.format(cname))
        local('git init')
        _hidden_run('git config user.email "{}"'.format(GH_USER_EMAIL))
        _hidden_run('git config user.name "{}"'.format(GH_USER_NAME))
        local('git checkout -b {}'.format(branch))
        local('git add -A .')
        local('git commit -a -m "Travis #{}"'.format(TRAVIS_BUILD_NUMBER))
        _hidden_run('git remote add origin https://{}@github.com/{}/{}'.format(
            GH_TOKEN,
            GH_USER_LOGIN,
            repo))
        _hidden_run('git push --quiet --force origin {} > /dev/null 2>&1'.format(branch))


def travis_push_github():
    if GIT_BRANCH == 'master':
        GH_CNAME = os.getenv('GH_CNAME')
        GH_PUSH_REPO = os.getenv('GH_PUSH_REPO')
        _travis_push_github(GH_PUSH_REPO, 'master', GH_CNAME)
    else:
        GH_CNAME = os.getenv('GH_CNAME_DEVEL')
        GH_PUSH_REPO = os.getenv('GH_PUSH_REPO_DEVEL')
        _travis_push_github(GH_PUSH_REPO, 'gh-pages', GH_CNAME)


@task
def test_web_compile():
    # Tries to deploy
    deploy_web()
    # If no error, it pushes to github
    travis_push_github()


def compress_images():
    local('smusher ./media/images')
    #local('jpegoptim --size=4700k *')
    local('find content -name "*.png" -exec pngcrush -ow {}')

#@hosts(PROD)
#def publish():
#    regen()
#    project.rsync_project(
#        remote_dir=DEST_PATH,
#        local_dir=DEPLOY_PATH.rstrip('/') + '/',
#        delete=True
#    )
