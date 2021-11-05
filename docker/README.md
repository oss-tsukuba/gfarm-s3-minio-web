# gfarm-s3-minio-web container

## 仕組み概要

- ホスト OS の各ユーザのディレクトリをコンテナ内に作成される
  - 各ユーザのホームディレクトリにある以下のファイルが利用される
    (シンボリックリンクでは動作しない)
    - .globus ディレクトリ
    - .gfarm_shared_key ファイル
    - .gfarm2rc ファイル
  - コンテナ内の /etc/grid-security/cetificates に置く証明書を指定
- WebUI が起動
- Gfarm ユーザ名と対応するパスワードでログイン
  - grid-proxy-init のパスフレーズ
  - myproxy-logon のパスワード
  - 共有鍵の場合: gfarm-s3-sharedsecret-password で得られるパスワード
- ユーザごとに minio を起動
- minio アクセスのシークレットは volume に保持される TODO

## 事前に決ておく

- SHARED_DIR: ユーザごとのバケット置き場とする Gfarm 上ディレクトリ

## 事前設定

- gfarm2.conf をこのディレクトリ置く
- 各ユーザは、ホームディレクトリに Gfarm, GSI (.globus) の設定をしておく
- certificates ディレクトリに信頼する証明書を置く
- gfarm-s3-usermap file
- docker-compose.override.yml を用意
  docker-compose.yml から自分の環境に合わせて上書き
  docker-compose.override.example-hpci.yml は HPCI 共用ストレージ向けの例
  シンボリックリンクでも良い
- gfarm-s3-usermap.conf 作成
  許可するローカルユーザと、Gfarm ユーザとの対応付け、
  および、S3 アクセスキーとの対応付けをおこなう
- CRL 取得スクリプト作成
  - 必要であればホスト OS 側で certificates 内の CRL を更新する
    ホスト OS 側の crontab などで定期実行すると良い

## 制限事項

- コンテナを再構築(reborn)する必要がある場合
  - docker-compose.yml 設定変更時
  - ユーザ対応が入れ替わる場合
  - gfarm-s3-minio-web 更新時
  - gfarm-s3-minio 更新時
- コンテナを再起動(restart)する必要がある場合
  - ユーザ増減時
  - ユーザのホームディレクトリ増減時

## 構築、更新 (ビルド時間含む)

make reborn
(起動ログが表示されるので起動後は ctrl-c で停止)

## コンテナイメージ再生成

make reborn-nocache

## 停止

make stop

## 再起動 (短時間)

make restart

## コンテナ内シェル

make shell
sudo -i -u ユーザ

## 永続情報も消す

make down-REMOVE_VOLUMES
