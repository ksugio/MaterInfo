# MaterInfo について
MaterInfo はマテリアルズ・インフォマティクスのためウェブアプリケーションである。
このアプリケーションを用いてデータの収集，特徴量抽出，特徴量取集，特徴量選択，機械学習および逆解析を実施することができる。
また，図の作成，参考文献の管理，文章のバージョン管理，スケジュール管理，アンケート機能，掲示板等の研究支援機能も充実している。

[https://www.youtube.com/@MaterInfo-lm8vk](https://www.youtube.com/@MaterInfo-lm8vk) にて使用法等を解説している。

# Windowsでの実行

Docker Desktop for Windowsを[サイト](https://matsuand.github.io/docs.docker.jp.onthefly/desktop/windows/install/)からダウンロードしてインストールする。

[compose.yaml](https://github.com/ksugio/MaterInfo/blob/main/compose.yaml)
をダウンロードして， それを適当な場所に配置する。
コマンドプロンプトを立ち上げ，compose.yamlのあるフォルダに移動して，
以下のコマンドでコンテナを作成・起動する。
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
sudo apt install pkg-config
```
仮想環境を作成して，仮想環境へ移行する。
```
python3 -m venv venv
cd venv
source bin/activate
```
ソースコードをダウンロードする。
```
git clone https://github.com/ksugio/MaterInfo.git
```
仮想環境へ必要なライブラリをインストールする。
```
(venv) pip install --upgrade pip
(venv) cd MaterInfo
(venv) pip install -r requirements.txt
```
データベースを作成する。
```
sudo mysql -u root
mysql> create user 'materinfouser'@'localhost' identified by 'materinfopw';
mysql> create database materinfo;
mysql> grant all privileges on materinfo.* to 'materinfouser'@'localhost';
mysql> flush privileges;
```
データベース名 materinfo，ユーザー名 materinfouser および パスワード materinfopw は適当に変更してください。
MaterInfo ディレクトリに 以下の内容で .env ファイルを作成する。
```
SECRET_KEY=v7u0e4hc403+rzi213ylbd5r@_oyrt-vtkf1aqpc9t=w-)0tkn
DEBUG=False
DATABASE_URL=mysql://materinfouser:materinfopw@localhost:3306/materinfo
STATIC_ROOT=/home/ksugio/static
MEDIA_ROOT=/home/ksugio/media
MEDIA_ACCEL_REDIRECT=True
REPOS_ROOT=/home/ksugio/repos
TEMP_ROOT=/home/ksugio/temp
CELERY_BROKER_URL=redis://localhost:6379

USE_LOCAL_HOST_CHECK=True
USE_LOCAL_HOST_HOSTS=https://mi.matphys.hiroshima-u.ac.jp
USE_LOCAL_HOST_LOCALHOST=http://localhost:8000
```
SECRET_KEYは適当な値に変更し， DEBUG を Falseに設定する。
DATABASE_URLのデータベース名，ユーザー名およびパスワードは先ほど登録したものを設定する。
STATIC_ROOT, MEDIA_ROOT, REPOS_ROOT, TEMP_ROOT を任意のディレクトリに設定する。
nginx の X-Accel-Redirect を使う場合は、MEDIA_ACCEL_REDIRECT=True とする。




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
