# About MaterInfo
MaterInfo is a web application for materials informatics.
This application can be used to collect data, extract features, collect features,
select features, machine learning, and perform inverse analysis.
It also has extensive research support functions such as diagram creation,
reference management, document version control, schedule management,
questionnaire functions, and bulletin boards.

[Japanese version README](README-ja.md)

# Run on Windows

Download and install Docker Desktop for Windows from [site](https://www.docker.com/products/docker-desktop/).

Download [compose.yaml](https://github.com/ksugio/MaterInfo/blob/main/compose.yaml)
and place it in an appropriate location.
Launch a command prompt, move to the folder where compose.yaml is located,
Create and start a Docker container with the following command.
```
docker compose up -d
```
Once the container has been successfully created and started, launch the materinfo shell.
````
docker compose exec materinfo /bin/bash
````
Perform migration, create administrative users, and collect static files.
````
(materinfo) python manage.py migrate
(materinfo) python manage.py createsuperuser
(materinfo) python manage.py collectstatic
````
Restart the Docker container.
When you access [http://localhost:8080/](http://localhost:8080/),
a login screen will appear, so log in with the administrator user you created.

# Deploy to Ubuntu22.04LTS

Python3 and git are installed.
Install nginx and mariaDB.
````
sudo apt update
sudo apt upgrade
sudo apt install nginx
sudo apt install mariadb-server
sudo apt install default-libmysqlclient-dev
````
Create a virtual environment and migrate to a virtual environment.
````
python3 -m venv venv
cd venv
source bin/activate
````
Install the required libraries to the virtual environment.
```
(venv) pip install --upgrade pip
(venv) pip install wheel
(venv) pip install Django==4.2
(venv) pip install MPLn23d
(venv) pip install MPImfp
(venv) pip install django-bootstrap5
(venv) pip install opencv-python
(venv) pip install pillow
(venv) pip install pandas
(venv) pip install matplotlib
(venv) pip install seaborn
(venv) pip install scikit-learn
(venv) pip install djangorestframework
(venv) pip install markdown
(venv) pip install django-filter
(venv) pip install djangorestframework-simplejwt
(venv) pip install djoser
(venv) pip install ldap3
(venv) pip install django-mdeditor
(venv) pip install diff-match-patch
(venv) pip install django_cleanup
(venv) pip install pybeads
(venv) pip install lmfit
(venv) pip install GitPython
(venv) pip install xgboost
(venv) pip install lightgbm
(venv) pip install optuna
(venv) pip install umap-learn
(venv) pip install skl2onnx
(venv) pip install onnxmltools
(venv) pip install onnxruntime
(venv) pip install shap
(venv) pip install django-environ
(venv) pip install mysqlclient==2.1.0
(venv) pip install uwsgi
```
Download source code.
```
git clone https://github.com/ksugio/MaterInfo.git
```
Create a database.
```
sudo mysql -u root
mysql> create user 'materinfouser'@'localhost' identified by 'materinfopw';
mysql> create database materinfo;
mysql> grant all privileges on materinfo.* to 'materinfouser'@'localhost';
mysql> flush privileges;
```
Change the database name (materinfo), user name (materinfouser),
and password (materinfopw) as appropriate.
Since MariaDB is used, comment out the sqlite3 setting in DATABASES in settings.py
and enable the mysql setting by using  the database name, user name,
and password that you registered earlier.
```
DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #}
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'materinfo',
        'USER': 'materinfouser',
        'PASSWORD': 'materinfopw',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```
Change SECRET_KEY to an appropriate value and set DEBUG to False.
```
SECRET_KEY = 'v7u0e4hc403+rzi213ylbd5r@_oyrt-vtkf1aqpc9t=w-)0tkn'
DEBUG = False
```
To change the data storage destination to /home/ubuntu/data, write as follows.
```
#DATA_DIR = BASE_DIR
DATA_DIR = '/home/ubuntu/data'
```
Also, configure as follows to use Nginx X-Accel-Redirect.
```
#MEDIA_ACCEL_REDIRECT = False
MEDIA_ACCEL_REDIRECT = True
```
When creating new migration files, run makemigrations for all applications.
Also, create an administrative user after migrating.
```
(venv) cd MaterInfo
(venv) python manage.py makemigrations accounts album article calendars collect \
 comment density document general hardness image material plot poll project \
 public reference repository sample schedule value
(venv) python manage.py migrate
(venv) python manage.py createsuperuser
```
Run makemigrations and migrate if migration files already exist.
```
(venv) cd MaterInfo
(venv) python manage.py makemigrations
(venv) python manage.py migrate
```
Change chdir in uwsgi.ini to the MaterInfo installation directory.
If MaterInfo is installed in /home/ubuntu/venv/MaterInfo, change as follows.
```
[uwsgi]
chdir = /home/ubuntu/venv/MaterInfo
module = config.wsgi:application
http = :8000
processes = 4
```
If you start the uwsgi server, access localhost:8000 in your browser,
and the login screen appears, the first step is successful.
```
(venv) uwsgi --ini uwsgi.ini
```
Next, change /etc/nginx/sites-available/default as follows.
```
server {
    listen 80;
    server_name 192.168.1.10;

    client_max_body_size 50m;

    location /static {
        alias /home/ubuntu/data/static;
    }

    location /media {
        internal;
        alias /home/ubuntu/data/media;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://localhost:8000;
        include /home/ubuntu/venv/MaterInfo/uwsgi_params;
    }
}
```
Restart Nginx.
```
sudo systemctl restart nginx
```
Add a file (uwsgi.service) with the following content to /etc/systemd/system
to automatically start the service.
```
[Unit]
Description=uWSGI service for MaterInfo

[Service]
ExecStart=/bin/bash -c 'source /home/ubuntu/venv/bin/activate; uwsgi --ini /home/ubuntu/venv/MaterInfo/uwsgi.ini'
ExecStop=/bin/kill -INT ${MAINPID}
Restart=no
KillSignal=SIGOUT

[Install]
WantedBy=multi-user.target
```
Start uwsgi(MaterInfo).
```
sudo systemctl start uwsgi
```
If you access the server with a browser and the top page is displayed,
the deployment is successful, and you can log in with the administrator user you created.
