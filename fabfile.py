import datetime
import socket

from fabric.api import *


env.use_ssh_config = True
env.host_string = 'ns'


def re():
    local('sudo systemctl restart gunicorn')


def up():
    local('django/manage.py runserver --insecure')


def static():
    local('django/manage.py collectstatic --noinput')


def md():
    local('django/manage.py cms_remarkdown')
    local('django/manage.py journal_remarkdown')


def get_backup_filename(hostname):
    return 'backups/{}_{}.json'.format(
        hostname,
        datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
    )

BACKUP_COMMAND = 'django/manage.py dumpdata cms journal uploads > '
def backup():
    """Does a local database dump. Returns the filename."""
    local_filename = get_backup_filename(hostname=socket.gethostname())
    local(BACKUP_COMMAND + local_filename)

    return local_filename


def backup_remote():
    """Does a remote database dump and scps the file. Returns the filename."""
    remote_filename = get_backup_filename(hostname=env.host_string)
    print("Remote filename: " + remote_filename)

    run(BACKUP_COMMAND + remote_filename)
    # scp the remote backup file to local.
    with cd('new-socialist'):
        get(remote_filename, remote_filename)

    return remote_filename


def media_backup():
    local('tar czvf media.tar.gz media')


def confirm_local():
    if socket.gethostname() == env.host_string:
        abort("You're on the remote machine (run this locally)")


# ONLY RUN THIS LOCALLY. Imports the remote database dump.
def imp():
    confirm_local()

    # First, backup locally.
    backup()

    # Then backup remotely & download the file.
    remote_filename = backup_remote()

    # Then run loaddata.
    local('django/manage.py loaddata ' + remote_filename)

    # Backup the local media dir then rsync with the remote dir.
    media_backup()
    local('rsync -Prz %s:new-socialist/media/ media/' % env.host_string)


# ONLY RUN THIS LOCALLY. Exports the local database dump.
def exp():
    confirm_local()

    # First, backup remotely & download the file.
    backup_remote()

    # Then backup locally.
    local_filename = backup()

    # Move the local dump over to remote.
    put(local_filename, 'new-socialist/backups')

    # Sync the media directories.
    local('rsync -Prz media/ %s:new-socialist/media/' % env.host_string)

    with cd('new-socialist'):
        # Then run loaddata.
        run('source env/bin/activate && django/manage.py loaddata ' + local_filename)

def deploy():
    confirm_local()
    local('git push')
    with cd('new-socialist'):
        run('git pull')
        sudo('systemctl restart gunicorn')


def migrate():
    local('django/manage.py makemigrations')
    local('django/manage.py migrate')
