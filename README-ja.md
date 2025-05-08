# MaterInfo について
MaterInfo はマテリアルズ・インフォマティクスのためウェブアプリケーションである。
このアプリケーションを用いてデータの収集，特徴量抽出，特徴量取集，特徴量選択，機械学習および逆解析を実施することができる。
また，図の作成，参考文献の管理，文章のバージョン管理，スケジュール管理，アンケート機能，掲示板等の研究支援機能も充実している。

[https://www.youtube.com/@MaterInfo-lm8vk](https://www.youtube.com/@MaterInfo-lm8vk) にて使用法等を解説している。

# Dockerでの実行

Windowsの場合，Docker Desktop for Windowsを[ウェブサイト](https://matsuand.github.io/docs.docker.jp.onthefly/desktop/windows/install/)からダウンロードしてインストールする。

Ubuntuの場合，Docker Engineを[ウェブサイト](https://matsuand.github.io/docs.docker.jp.onthefly/engine/install/ubuntu/)を参考にインストールする。

[compose.yaml](https://github.com/ksugio/MaterInfo/blob/main/compose.yaml)
をダウンロードして， それを適当な場所に配置する。
コマンドプロンプト（ターミナル）を立ち上げ，compose.yamlのあるフォルダに移動して，
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

Python3およびgitはインストール済みとする。
Nginx, MariaDB および Redis をインストールする。
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

static, media, repos, temp ファイルの置き場所を準備する。
```
mkdir /home/ubuntu/data/static
mkdir /home/ubuntu/data/media
mkdir /home/ubuntu/data/repos
mkdir /home/ubuntu/data/temp
```
MaterInfo ディレクトリに 以下の内容で .env ファイルを作成する。
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
SECRET_KEYは適当な値に変更し， DEBUG を Falseに設定する。
DATABASE_URLのデータベース名，ユーザー名およびパスワードは先ほど登録したものを設定する。
STATIC_ROOT, MEDIA_ROOT, REPOS_ROOT, TEMP_ROOT を準備したディレクトリに設定する。
Nginx の X-Accel-Redirect を使う場合は、MEDIA_ACCEL_REDIRECT を True とする。
USE_LOCAL_HOST_CHECK を True にすると、内部でURLの読み替えを行う。
USE_LOCAL_HOST_HOSTS で指定したURLは USE_LOCAL_HOST_LOCALHOST で指定したURLに読み替えられる。
これは，ローカルホスト内のAPI を使った処理をローカルホスト内で完結させるための設定である。

電子メールを使用する場合はメールサーバーを準備して、 .env に以下の設定を追加する。
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
マイグレート，管理ユーザー作成，静的ファイル収集を実行する。
```
(venv) python manage.py migrate
(venv) python manage.py createsuperuser
(venv) python manage.py collectstatic
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
    server_name host.name;

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
        include /home/ubuntu/venv/MaterInfo/nginx/uwsgi_params;
    }
}
```
ここで，host.name, /home/ubuntu/data/static, /home/ubuntu/data/media, /home/ubuntu/venv/MaterInfo/uwsgi_params は環境に合わせて設定する。

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
ここで，/home/ubuntu/venv/bin/activate, /home/ubuntu/venv/MaterInfo/uwsgi.ini は環境に合わせて設定する。

uwsgi(アプリケーション・サーバー)の自動起動を有効化する。また、起動する。
```
sudo systemctl enable uwsgi
sudo systemctl start uwsgi
```
また，ワーカーを自動起動するために /etc/systemd/system に以下の内容でファイル（celery.service）を追加する。
```
Description=Celery service for MaterInfo
After=network.target

[Service]
WorkingDirectory=/home/ubuntu/venv/MaterInfo
ExecStart=/bin/bash -c 'source /home/ubuntu/venv/bin/activate; celery -A config worker -Q project,collect --concurrency=1'
ExecStop=/bin/kill -INT ${MAINPID}
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```
ここで，/home/ubuntu/venv/MaterInfo, /home/ubuntu/venv/bin/activate  は環境に合わせて設定する。

celery(ワーカー)の自動起動を有効化する。また、起動する。
```
sudo systemctl enable celery
sudo systemctl start celery
```
ブラウザでサーバーにアクセスしてトップページが表示されればデプロイは成功。 作成した管理ユーザーでログインする。