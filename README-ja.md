# MaterInfo について
MaterInfo はマテリアルズ・インフォマティクスのためウェブアプリケーションである。
このアプリケーションを用いてデータの収集，特徴量抽出，特徴量取集，特徴量選択，機械学習および逆解析を実施することができる。
また，図の作成，参考文献の管理，文章のバージョン管理，スケジュール管理，アンケート機能，掲示板等の研究支援機能も充実している。

[https://www.youtube.com/@MaterInfo-lm8vk](https://www.youtube.com/@MaterInfo-lm8vk) にて使用法等を解説してる。

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
