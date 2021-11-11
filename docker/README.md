# gfarm-s3-minio-web container

## 仕組み概要

- Gfarm S3 の仕組みをコンテナ内に構築する
- ホスト OS の各一般ユーザが S3 互換 IF で Gfarm にアクセスできる
- ユーザごとに専用ディレクトリがコンテナ内にも作成される
  - 各ユーザのホームディレクトリにある以下のファイルが利用される
    (以下はシンボリックリンクになっていると動作しないことに注意)
    - .globus ディレクトリ
    - .gfarm_shared_key ファイル
    - .gfarm2rc ファイル
- /etc/grid-security/cetificates に置く証明書をコンテナ起動時に指定
- gfarm2.conf をコンテナ起動時に指定
- コンテナを起動すると WebUI が起動
- WebUI に各ユーザがアクセスし Gfarm ユーザ名と対応するパスワードでログイン
  - myproxy-logon のパスワード
  - grid-proxy-init のパスフレーズ
  - 共有鍵の場合は gfarm-s3-sharedsecret-password で得られるパスワード
- ユーザごとにボタンを押して minio を起動
- アクセスキーID、シークレットアクセスキーを表示
  - S3 クライアントに設定し、minio を経由して Gfarm にアクセス
- シークレットアクセスキーは自動生成され、ランダムな値で更新可能
- 共有設定
  - バケットごとに他ユーザにアクセスを許可設定可能
    - S3 クライアントからは sss バケット経由で見える
- コンテナ再起動・再構築後に起動状態をなるべく維持
  - Gfarm の認証が期限切れの場合は停止状態で起動
    (Gfarm 認証不可の場合 minio を起動できないため)
    (もし起動できたとしても、再ログインするまで利用不可)
  - 期限切れの場合、各ユーザが再度 WebUI にログインしてから minio を起動

## 事前に決ておくこと

- SHARED_DIR: ユーザごとのバケット置き場とする Gfarm 上ディレクトリ
  - Gfarm の管理者に依頼し、作成する
  - 各ユーザごとに Gfarm ユーザ名のディレクトリをそこに作成する
  - モードは 0755
  - 所有は、そのユーザ:gfarmadm

## 事前設定

- 各ユーザは、ホスト OS のホームディレクトリ以下に設定
  - Gfarm の設定
  - GSI (.globus) の設定
- gfarm2.conf をこのディレクトリに置く
- certificates ディレクトリに信頼する証明書を入れ、このディレクトリに置く
- gfarm-s3-usermap ファイルを作成し、このディレクトリに置く
  各行に
  <Gfarm Username>:<Local Username>:<S3 Accesskey ID>
  を列挙する
- docker-compose.override.yml を作成し、このディレクトリに置く
  docker-compose.yml から自分の環境に合わせて上書き
  docker-compose.override.example-hpci.yml は HPCI 共用ストレージ向けの例
  シンボリックリンクでも良い
- gfarm-s3-usermap.conf 作成
  許可するローカルユーザと、Gfarm ユーザとの対応付け、
  および、S3 アクセスキーとの対応付けをおこなう
- CRL 取得スクリプト作成
  - 必要であればホスト OS 側で certificates 内の CRL を更新する
    ホスト OS 側の crontab などで定期実行すると良い

## 永続化される情報

以下が Docker volume に保存される。

- 各ユーザの S3 シークレットアクセスキー
- 各ユーザの X509_USER_PROXY ファイル
- 各ユーザのサービス起動状態
- TODO マルチパートアップロード用一時ファイル

ホスト OS 側にある Gfarm 関連ファイル、GSI 関連ファイルはコンテナ内に
は保管されない。

## 構築、更新 (ビルド時間含む)

make reborn

ログを表示しながら起動 (起動後は ctrl-c で停止)
make reborn-withlog

## コンテナイメージ再生成

make reborn-nocache

## 停止

make stop

## 再起動 (短時間)

make restart

ログを表示しながら起動 (起動後は ctrl-c で停止)
make restart-withlog

## コンテナ内シェル

make shell
sudo -i -u ユーザ

## 永続情報も消す

make down-REMOVE_VOLUMES

## メンテナンス

- コンテナを再構築(reborn)する必要がある場合
  - docker-compose.yml 設定変更時
  - ユーザ対応が入れ替わる場合
  - gfarm-s3-minio-web 更新時
  - gfarm-s3-minio 更新時
- コンテナを再起動(restart)する必要がある場合
  - ユーザ増減時
  - ユーザのホームディレクトリ増減時

## 永続情報のバックアップ、リストア

TODO
