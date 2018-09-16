New Socialist
=============

Django site for managing an online publication.

## Setup

Within a virtualenv, run the following commands, in order:

```bash
pip install -r requirements.txt
./django/manage.py makemigrations journal cms uploads
./django/manage.py migrate
./django/manage.py createsuperuser
./django/manage.py loaddata initial_fixtures.json
```

Finally:

`./django/manage.py runserver`

You can find the admin interface at <http://localhost:8000/sudo/> (for the
superuser) or <http://localhost:8000/editor/> (the link to give to editors).
You can create users with editor permissions via the /sudo/ admin site:
set `is_staff` to True, and give them any necessary permissions (there will
be a permission group eventually, but for now you'll have to select them
manually).

None of the links in the menu will work. You'll have to create the 4 categories
(under the journal app) and the 2 pages (under the cms app).

## Deploying in production

To deploy in production with Postgres, a custom secret key, and DEBUG=False,
set the following environment variables within the virtualenv:

* `POSTGRES_PASSWORD`: the password for PostgreSQL
* `DJANGO_SECRET_KEY`: the `SECRET_KEY` used by Django (set to a random string)
* `ALLOWED_HOST`: e.g., 'newsocialist.org.uk'

### systemd

Currently running as a systemd service. Create
/etc/systemd/system/gunicorn.service:

```
[Unit]
Description=gunicorn daemon for newsocialist
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/path/to/dir/new-socialist/django
EnvironmentFile=/path/to/dir/new-socialist/env/bin/variables
ExecStart=/path/to/dir/new-socialist/env/bin/gunicorn --access-logfile - --workers 3
--bind unix:/tmp/gunicorn.sock newsocialist.wsgi:application

[Install]
WantedBy=multi-user.target
```

The `variables` file should look something like this:

```
ALLOWED_HOST='newsocialist.org.uk'
POSTGRES_PASSWORD='password'
DJANGO_SECRET_KEY='secretkey'
SENDGRID_PASSWORD='password'
```

Restart the service by running `fab re`.

### nginx

The configuration file should look something like this:

```
server {
    listen 80;

    if ($host = newsocialist.org.uk) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = www.newsocialist.org.uk) {
        return 301 https://newsocialist.org.uk$request_uri;
    }

    server_name newsocialist.org.uk www.newsocialist.org.uk;
    return 404; # managed by Certbot
}


server {
    listen 443 default_server ssl;
    server_name newsocialist.org.uk;

    location /favicon.ico {
        alias /path/to/dir/new-socialist/static/favicon.ico;
    }

    location /media/ {
        root /path/to/dir/new-socialist;
    }

    location /static/ {
        root /path/to/dir/new-socialist;
    }

    location / {
        client_max_body_size 15M;
        include proxy_params;
        proxy_pass http://unix:/tmp/gunicorn.sock;
    }

    # for certbot renewal
    location ~ /.well-known {
        root /path/to/dir/new-socialist;
        allow all;
    }

    ssl_certificate /etc/letsencrypt/live/newsocialist.org.uk/fullchain.pem; #
managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/newsocialist.org.uk/privkey.pem; # managed by Certbot

    # deny illegal host headers to prevent "Invalid HTTP_HOST header" emails
    if ($host !~* ^newsocialist.org.uk$ ) {
        return 444;
    }
}
```
