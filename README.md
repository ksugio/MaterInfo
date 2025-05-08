# About MaterInfo
MaterInfo is a web application for materials informatics.
This application can be used for data collection, feature extraction, feature collection, feature selection, machine learning, and inverse analysis.
In addition, it has a full range of research support functions such as diagram creation, reference management, text version management, schedule management, questionnaire function, bulletin board, and so on.

[Japanese version README](README-ja.md)

# Run on Docker

For Windows, download and install Docker Desktop for Windows from [site](https://docs.docker.com/desktop/setup/install/windows-install/).

For Ubuntu, install Docker Engine by referring to the website [site](https://docs.docker.com/engine/install/ubuntu/).

Download [compose.yaml](https://github.com/ksugio/MaterInfo/blob/main/compose.yaml)
and place it in an appropriate location.
Open a command prompt, go to the folder where compose.yaml is located, and run the following commands to create a container.
```
docker compose up -d
```
After the container is successfully created and started, launch the materinfo shell.
```
docker compose exec materinfo /bin/bash
```
Run migrate, create admin user, and collect static files.
```
(materinfo) python manage.py migrate
(materinfo) python manage.py createsuperuser
(materinfo) python manage.py collectstatic
```
When you access [http://localhost:8080/](http://localhost:8080/),
a login screen will appear, so log in with the administrator user you created.

# Deploy to Ubuntu22.04LTS

Python3 and git should be already installed.
Install Nginx, MariaDB and Redis.
```
sudo apt update
sudo apt upgrade
sudo apt install nginx
sudo apt install mariadb-server
sudo apt install redis-server
sudo apt install default-libmysqlclient-dev
sudo apt install pkg-config
sudo apt install texlive-latex-extra texlive-science texlive-publishers latexmk
sudo apt install texlive-lang-japanese
```
Create a virtual environment and migrate to the virtual environment.
```
python3 -m venv venv
cd venv
source bin/activate
```
Download the source code.
```
git clone https://github.com/ksugio/MaterInfo.git
```
Install the necessary libraries into the virtual environment.
```
(venv) pip install --upgrade pip
(venv) cd MaterInfo
(venv) pip install -r requirements.txt
``` 
Create the database.
```
sudo mysql -u root
mysql> create user 'materinfouser'@'localhost' identified by 'materinfopw';
mysql> create database materinfo;.
mysql> grant all privileges on materinfo.* to 'materinfouser'@'localhost';
mysql> flush privileges; mysql> flush privileges;
```
Change the database name (materinfo), the user name (materinfouser) and the password (materinfopw) as appropriate.

Prepare the placement of the static, media, repos, and temp files.
````
mkdir /home/ubuntu/data/static
mkdir /home/ubuntu/data/media
mkdir /home/ubuntu/data/repos
mkdir /home/ubuntu/data/temp
````
Create an .env file in the MaterInfo directory with the following contents.
```
SECRET_KEY=v7u0e4hc403+rzi213ylbd5r@_oyrt-vtkf1aqpc9t=w-)0tkn
DEBUG=False
DATABASE_URL=mysql://materinfouser:materinfopw@localhost:3306/materinfo
STATIC_ROOT=/home/ubuntu/data/static
MEDIA_ROOT=/home/ubuntu/data/media
MEDIA_ACCEL_REDIRECT=True
REPOS_ROOT=/home/ubuntu/data/repos
TEMP_ROOT=/home/ubuntu/data/temp
USE_LOCAL_HOST_CHECK=True
USE_LOCAL_HOST_HOSTS=https://host.name
USE_LOCAL_HOST_LOCALHOST=http://localhost:8000
```
Change SECRET_KEY to an appropriate value and set DEBUG to False.
Set the database name, user name, and password in DATABASE_URL to the ones you have just registered.
Set STATIC_ROOT, MEDIA_ROOT, REPOS_ROOT, and TEMP_ROOT to the prepared directories.
If you use Nginx's X-Accel-Redirect, set MEDIA_ACCEL_REDIRECT to True.
If USE_LOCAL_HOST_CHECK is set to True, URLs are reread internally.
The URL specified by USE_LOCAL_HOST_HOSTS is replaced by the URL specified by USE_LOCAL_HOST_LOCALHOST.
This is a setting to complete processing using APIs in the local host.

To use e-mail, prepare a mail server and add the following configuration to .env.
```
EMAIL_ACTIVE=True
EMAIL_HOST=email.host
EMAIL_HOST_USER=user@email.host
EMAIL_HOST_PASSWORD=password
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=user@email.host
```
Perform migrate, create admin user, and static file collection.
```
(venv) python manage.py migrate
(venv) python manage.py createsuperuser
(venv) python manage.py collectstatic
```
Change chdir in uwsgi.ini to the MaterInfo installation directory.
When MaterInfo is installed in /home/ubuntu/venv/MaterInfo, change as follows.
````
[uwsgi].
chdir = /home/ubuntu/venv/MaterInfo
module = config.wsgi:application
http = :8000
processes = 4
````
If the uwsgi server is up and running, access localhost:8000 with a browser and the login screen appears, the first step is successful.
```
(venv) uwsgi --ini uwsgi.ini
```
Next, change /etc/nginx/sites-available/default as follows.
```
server {
    listen 80;
    server_name host.name;

    client_max_body_size 50m;

    location /static {
        alias /home/ubuntu/data/static; }
    }

    location /media {
        internal; }
        alias /home/ubuntu/data/media; }
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://localhost:8000;
        include /home/ubuntu/venv/MaterInfo/nginx/uwsgi_params;
    }
}
```
where host.name, /home/ubuntu/data/static, /home/ubuntu/data/media, and /home/ubuntu/venv/MaterInfo/uwsgi_params are set according to the environment.

Restart Nginx.
```
sudo systemctl restart nginx
```
Add a file (uwsgi.service) to /etc/systemd/system with the following contents to start the service automatically.
```
[Unit].
Description=uWSGI service for MaterInfo

[Service]
ExecStart=/bin/bash -c 'source /home/ubuntu/venv/bin/activate; uwsgi --ini /home/ubuntu/venv/MaterInfo/uwsgi.ini'
ExecStop=/bin/kill -INT ${MAINPID}
Restart=no
KillSignal=SIGOUT

[Install]
WantedBy=multi-user.target
```
where /home/ubuntu/venv/bin/activate and /home/ubuntu/venv/MaterInfo/uwsgi.ini should be set according to your environment.

Enable automatic start-up of uwsgi (application server). Also start.
```
sudo systemctl enable uwsgi
sudo systemctl start uwsgi
```
Also, add a file (celery.service) to /etc/systemd/system with the following contents to start the worker automatically.
```
Description=Celery service for MaterInfo
After=network.target

[Service].
WorkingDirectory=/home/ubuntu/venv/MaterInfo
ExecStart=/bin/bash -c 'source /home/ubuntu/venv/bin/activate; celery -A config worker -Q project,collect --concurrency=1'
ExecStop=/bin/kill -INT ${MAINPID}
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```
where /home/ubuntu/venv/MaterInfo and /home/ubuntu/venv/bin/activate should be set according to your environment.

Enable automatic start-up of celery (worker). Also start.
```
sudo systemctl enable celery
sudo systemctl start celery
```
Access the server with a browser, and if the top page is displayed, the deployment has succeeded.
Log in as the created administrative user.