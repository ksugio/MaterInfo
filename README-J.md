# MaterInfo について
MaterInfo はマテリアルズ・インフォマティクスのためウェブアプリケーションである。
このアプリケーションを用いてデータの収集，特徴量抽出，特徴量取集，特徴量選択，機械学習および逆解析を実施することができる。
また，図の作成，参考文献の管理，文章のバージョン管理，スケジュール管理，アンケート機能，掲示板等の研究支援機能も充実している。

# Windowsでの実行

Docker Desktop for Windowsを[サイト](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)からダウンロードしてインストールする。

[https://github.com/ksugio/MaterInfo](https://github.com/ksugio/MaterInfo) にアクセスして，
[Code] - [Download ZIP] でソースコードをダウンロードして， それを適当な場所に展開する。
コマンドプロンプトを立ち上げ， 展開した（compose.yamlのある）フォルダに移動して， 以下のコマンドでコンテナを作成・起動する。
```
docker compose up -d
```
コンテナの作成・起動が成功したら，materinfoのシェルを立ち上げる。
```
docker compose exec materinfo /bin/bash
```
マイグレート，管理ユーザー作成，静的ファイル収集を実行する。
```
(materinfo) python manage.py migrate
(materinfo) python manage.py createsuperuser
(materinfo) python manage.py collectstatic
```
Dockerコンテナを再起動して
[http://localhost:8080/](http://localhost:8080/) にアクセスするとログイン画面が現れるので，作成した管理ユーザーでログインする。

# Windowsでの開発環境の構築

Python（64ビット版）のファイルを[サイト](https://www.python.org/downloads/windows/)からダウンロードしてインストール

コマンドプロンプトから仮想環境を作成して，仮想環境へ移行
```
python -m venv venv
cd venv
Scripts\activate.bat
```
仮想環境へ必要なライブラリをインストール
```
pip install -r requirements.txt
```
以下の通り１つ１つインストールすることもできる。
```
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
```
ソースコードを [https://github.com/ksugio/MaterInfo](https://github.com/ksugio/MaterInfo)
からダウンロードして venv フォルダーに展開する。 Git を使う場合のコマンドは以下の通り。
```
git clone https://github.com/ksugio/MaterInfo.git
```
マイグレーションファイルを新規作成する場合はすべてのアプリケーションに対して makemigrations を実行する。
また，migrate の後，管理ユーザーを作成する。
```
(venv) cd MaterInfo
(venv) python manage.py makemigrations accounts album article calendars collect \
 comment density document general hardness image material plot poll project \
 public reference repository sample schedule value
(venv) python manage.py migrate
(venv) python manage.py createsuperuser
```
マイグレーションファイルが既に存在する場合は makemigrations および migrate を実行する。
```
(venv) cd MaterInfo
(venv) python manage.py makemigrations
(venv) python manage.py migrate
```
サーバーを立ち上げて
```
(venv) python manage.py runserver
```
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)にブラウザでアクセスしてトップページが表示されればインストールは成功

# Dockerイメージの作成

Docker Desktop for Windowsを[サイト](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)からダウンロードしてインストール

settings.pyのDATABASESのsqlite3の設定をコメントアウトして，
環境変数からデータベースを設定できるように変更する。
```
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
       'ENGINE': os.environ['DATABASE_ENGINE'],
       'NAME': os.environ['DATABASE_NAME'],
       'USER': os.environ['DATABASE_USER'],
       'PASSWORD': os.environ['DATABASE_PASSWORD'],
       'HOST': os.environ['DATABASE_HOST'],
       'PORT': os.environ['DATABASE_PORT'],
       'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
       }
    }
}
```
SECRET_KEY および DEBUG も環境変数から設定できるように変更する。
```
#SECRET_KEY = 'v7u0d4hc403)rzi253ylbd5r@_oynt-vokf1aqpc8t=w-)0tkn'
SECRET_KEY = os.environ['SECRET_KEY']

#DEBUG = True
DEBUG = bool(strtobool(os.environ['DEBUG']))
```
また，データの保存先を以下のように設定する。
```
#DATA_DIR = BASE_DIR
DATA_DIR = '/data'
```
さらに，NginxのX-Accel-Redirectを利用するために以下のように設定する。
```
#MEDIA_ACCEL_REDIRECT = False
MEDIA_ACCEL_REDIRECT = True
```
compose.yaml の materinfo セクションの "image" を "build" に変更する。
```
    #image: ksugio/materinfo:latest
    build: .
```
コマンドプロンプトを立ち上げ， ルートフォルダに移動してコンテナを作成・起動する。
```
docker compose up -d
```
コンテナの作成・起動が成功したら，materinfoのシェルを立ち上げる。
```
docker compose exec materinfo /bin/bash
```
マイグレート，管理ユーザー作成，静的ファイル収集を実行する。
```
(materinfo) python manage.py migrate
(materinfo) python manage.py createsuperuser
(materinfo) python manage.py collectstatic
```
Dockerコンテナを再起動して
[http://localhost:8080/](http://localhost:8080/) にアクセスするとログイン画面が現れるので，作成した管理ユーザーでログインする。

# Ubuntu22.04LTSへのデプロイ

Python3およびgitはインストール済み。
nginxおよびmariaDBをインストールする。
```
sudo apt update
sudo apt upgrade
sudo apt install nginx
sudo apt install mariadb-server
sudo apt install default-libmysqlclient-dev
```
仮想環境を作成して，仮想環境へ移行
```
python3 -m venv venv
cd venv
source bin/activate
```
仮想環境へ必要ライブラリをインストール
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
(venv) pip install mysqlclient==2.1.0
(venv) pip install uwsgi
```
ソースコードをダウンロードする
```
git clone https://github.com/ksugio/MaterInfo.git
```
データベースの作成
```
sudo mysql -u root
mysql> create user 'materinfouser'@'localhost' identified by 'materinfopw';
mysql> create database materinfo;
mysql> grant all privileges on materinfo.* to 'materinfouser'@'localhost';
mysql> flush privileges;
```
データベース名 materinfo，ユーザー名 materinfouser および パスワード materinfopw は適当に変更してください。
MariaDB を使用するので，settings.py の DATABASES の sqlite3 の設定をコメントアウトして，mysql の設定を有効にする。
データベース名，ユーザー名およびパスワードは先ほど登録したものを設定する。
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
SECRET_KEYを適当な値に変更し， DEBUG を Falseに設定する。
```
SECRET_KEY = 'v7u0e4hc403+rzi213ylbd5r@_oyrt-vtkf1aqpc9t=w-)0tkn'
DEBUG = False
```
データの保存先を /home/ubuntu/data に変更する場合は以下のように記述する。
```
#DATA_DIR = BASE_DIR
DATA_DIR = '/home/ubuntu/data'
```
また，NginxのX-Accel-Redirectを利用するために以下のように設定する。
```
#MEDIA_ACCEL_REDIRECT = False
MEDIA_ACCEL_REDIRECT = True
```
マイグレーションファイルを新規作成する場合はすべてのアプリケーションに対して makemigrations を実行する。
また，migrate の後，管理ユーザーを作成する。
```
(venv) cd MaterInfo
(venv) python manage.py makemigrations accounts album article calendars collect \
 comment density document general hardness image material plot poll project \
 public reference repository sample schedule value
(venv) python manage.py migrate
(venv) python manage.py createsuperuser
```
マイグレーションファイルが既に存在する場合は makemigrations および migrate を実行する。
```
(venv) cd MaterInfo
(venv) python manage.py makemigrations
(venv) python manage.py migrate
```
uwsgi.ini の chdir を MaterInfo のインストールディレクトリに変更する。
MaterInfo が /home/ubuntu/venv/MaterInfo にインストールされている場合，以下のように変更する。
```
[uwsgi]
chdir = /home/ubuntu/venv/MaterInfo
module = config.wsgi:application
http = :8000
processes = 4
```
uwsgi サーバーを立ち上げ，ブラウザで localhost:8000 にアクセスしてログイン画面が現れれば，第一段階は成功。
```
(venv) uwsgi --ini uwsgi.ini
```
次に，/etc/nginx/sites-available/default を以下のように変更する。
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
Nginx を再起動する。
```
sudo systemctl restart nginx
```
サービスを自動起動するために /etc/systemd/system に以下の内容でファイル（uwsgi.service）を追加する。
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
uwsgi(MaterInfo)を起動する。
```
sudo systemctl start uwsgi
```
ブラウザでサーバーにアクセスしてトップページが表示されればデプロイは成功， 作成した管理ユーザーでログインする。

# サーバーの移動
移行元でデータベースのバックアップ
```
(venv) python manage.py dumpdata --exclude contenttypes > dump.json
```
メディアファイルとリポジトリのバックアップ
```
tar cvfz media.tgz media
tar cvfz repos.tgz repos
```
移行先でマイグレート後にリストア
```
(venv) python manage.py migrate
(venv) python manage.py loaddata dump.json
```
移行先でメディアファイルとリポジトリを展開する
```
tar xvfz media.tgz
tar xvfz repos.tgz
```