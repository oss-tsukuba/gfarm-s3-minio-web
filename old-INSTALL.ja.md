# Gfarm S3 インストール手順書

## 概要

Gfarm S3 is a S3 compatible object server for Gfarm.

Gfarm S3は、以下のコンポーネントから構成される。

* Gfarm 対応 S3 互換サーバ (MinIO)
* リバースプロキシ (Apache など)
* wsgi サーバ (gunicorn) (WebUI, Router で 2 個のポートを使用)
* WebUI フレームワーク (Django)

以下の前提・制限事項がある。

* myproxy server を使用する場合、Gfarm ユーザ名と myproxy ユーザ名が一
  致していること

インストール手順の概要は以下の通り。

0. 事前準備
  * _gfarm_s3 ユーザ・グループ作成
  * 依存パッケージのインストール
  * リバースプロキシの設定
  * WebUIフレームワークを動作させるユーザを作成

1. Gfarm S3のソースコードから以下のコンポーネントを自動インストール
  * WebUI フレームワーク (Django) を利用したページ
  * Gfarm 対応 S3 互換サーバ (MinIO)
  * gunicorn用のsystemdファイル
  * sudo の設定

2. リバースプロキシにGfarm S3用の設定を追加

3. gunicornサービス(2種)を起動

4. Gfarmファイルシステム上に必要なディレクトリを作成

### インストール手順

本手順はCentOS 7およびCentOS8で動作を確認した。

インストールは、Gfarm 2.7 (以降) のクライアントがインストール・設定さ
れている環境で行う。ホストの管理権限 (root) およびGfarmの管理者権限
(gfarmadm) が必要となる。

#### _gfarm_s3 ユーザ・グループを作成

実行例

```
groupadd -K GID_MIN=100 _gfarm_s3
useradd -K UID_MIN=100 -m _gfarm_s3 -g _gfarm_s3 -d /home/_gfarm_s3
```

#### Gfarm-S3をビルドするための作業ディレクトリを作成
(インストール後は削除して構わないのでどこでもよい)

```
WORKDIR=$HOME/tmp
mkdir -p $WORKDIR
MINIO_BUILDDIR=$HOME/tmp
mkdir -p $MINIO_BUILDDIR/minio/work/build
```

#### Gfarm S3のソースコードを入手する

```
(cd $WORKDIR &&
 git clone git@github.com:oss-tsukuba/gfarm-s3-minio-web.git)
(cd $WORKDIR/gfarm-s3-minio-web &&
 git checkout develop)

(cd $MINIO_BUILDDIR/minio/work/build &&
 git clone git@github.com:oss-tsukuba/gfarm-s3-minio.git)
(cd $MINIO_BUILDDIR/minio/work/build/gfarm-s3-minio &&
 git checkout gfarm)
```

#### 準備

##### パラメータを決める

以下のパラメータを決めておく。
これらは、configureにより$GFARM_S3_PREFIX/etc/gfarm-s3.conf
に反映させる。

```
GFARM_S3_PREFIX=/usr/local        # Gfarm-S3をインストールする場所
SHARED_DIR=/share                 # Gfarm-S3に使用するGfarm上のディレクトリ
CACHE_BASEDIR=/mnt/cache          # マルチパート作業用キャッシュディレクトリ
CACHE_SIZE=1024                   # 1ユーザあたりのキャッシュサイズ(MB)
GFARM_S3_USERNAME=_gfarm_s3       # WebUI,ルーターを実行するローカルユーザ名
GFARM_S3_GROUPNAME=_gfarm_s3      # そのグループ
GFARM_S3_HOMEDIR=/home/_gfarm_s3  # そのホームディレクトリ
WEBUI_ADDR=127.0.0.1:8000         # WebUIの待ち受けアドレス
ROUTER_ADDR=127.0.0.1:8001        # その待ち受けアドレス
MYPROXY_SERVER=                   # myproxy-logon使用時にサーバ名を指定
```

#### 依存パッケージをインストールする (CentOS 7 の例)

```
sudo yum update -y
sudo yum install -y uuid myproxy \
         python3-devel python3-pip nodejs
### フロントエンドに Apache を使用する場合
sudo yum install -y httpd mod_ssl
### フロントエンドに NGINX を使用する場合
sudo yum install -y nginx
sudo python3 -m pip install Django
sudo python3 -m pip install gunicorn
```

テスト実行時に必要
```
sudo python3 -m pip install boto3
```

#### 依存パッケージをインストールする (Ubuntu の例)

```
sudo apt-get install -y uuid myproxy python3 python3-pip python3-dev npm
### フロントエンドに Apache を使用する場合
sudo apt-get install -y apache2
### フロントエンドに NGINX を使用する場合
sudo apt-get install -y nginx
```

#### リバースプロキシとしてNGINXの設定例

XXX TODO

#### リバースプロキシとしてApacheの設定例

既にインストールされていれば本作業は不要

##### Apacheの設定ファイルを置く場所を決める
```
HTTPD_CONF=/etc/httpd/conf.d/myserver.conf
HTTPD_COMMON_CONF=/etc/httpd/conf.d/myserver-common.conf
HTTPD_DocumentRoot=/usr/local/share/www
```

##### Apacheの設定ファイルを作成

設定例

```
cat <<EOF | sudo dd of=$HTTPD_CONF
ServerName client1
<VirtualHost *:80>
        Include /etc/apache2/sites-available/myserver-common.conf
</VirtualHost>

<VirtualHost *:443>
        SSLEngine on
        SSLCertificateFile /etc/ssl/server/server.crt
        SSLCertificateKeyFile /etc/ssl/server/server.key
        Include /etc/apache2/sites-available/myserver-common.conf
</VirtualHost>
EOF
```

```
cat <<EOF | sudo dd of=$HTTPD_COMMON_CONF
DocumentRoot /usr/local/share/www
ServerAdmin root@localhost
CustomLog /var/log/apache2/access_log common
ErrorLog /var/log/apache2/error_log

<Directory "/usr/local/share/www">
        AllowOverride FileInfo AuthConfig Limit Indexes
        Options MultiViews Indexes SymLinksIfOwnerMatch Includes
        AllowOverride All
        Require all granted
</Directory>
EOF
```

##### Apacheのメインインデックスを作成
```
sudo mkdir -p $HTTPD_DocumentRoot
echo "gfarm -- $(date)" | sudo dd of=$HTTPD_DocumentRoot/index.html
```

##### Apacheを有効化する
```
sudo systemctl enable httpd
```

#### インストール

##### 作業ディレクトリに移動し configure

パラメータは上で決定したものを使用し、
with-gfarm, with-globus, with-myproxy,
with-apache, with-gunicornはそれぞれのインストール
プレフィックスを指定する。

```
(cd $WORKDIR/gfarm-s3-minio-web && ./configure \
	--prefix=$GFARM_S3_PREFIX \
	--with-gfarm=/usr/local \
	--with-globus=/usr \
	--with-myproxy=/usr \
	--with-gunicorn=/usr/local \
	--with-gfarm-s3-homedir=$GFARM_S3_HOMEDIR \
	--with-gfarm-s3-user=$GFARM_S3_USERNAME \
	--with-gfarm-s3-group=$GFARM_S3_GROUPNAME \
	--with-webui-addr=$WEBUI_ADDR \
	--with-router-addr=$ROUTER_ADDR \
	--with-cache-basedir=$CACHE_BASEDIR \
	--with-cache-size=$CACHE_SIZE \
	--with-myproxy-server=$MYPROXY_SERVER \
	--with-gfarm-shared-dir=$SHARED_DIR \
	--with-minio-builddir=$MINIO_BUILDDIR)
```

##### Go を作業ディレクトリにインストールする
```
(cd $WORKDIR/gfarm-s3-minio-web/minio && make install-go)
```

##### Gfarm-S3をビルドする
```
(cd $WORKDIR/gfarm-s3-minio-web && make)
```

##### Gfarm-S3をインストールする
```
(cd $WORKDIR/gfarm-s3-minio-web && sudo make install)
```

GFARM_S3_PREFIX ディレクトリ以下のファイル以外に、下記が追加される。

* /etc/sudoers.d/gfarm-s3
* gfarm-s3-webui.service, gfarm-s3-router.service (systemd 用)
* /home/_gfarm_s3/ 以下にファイル

#### Gfarm-S3の設定

##### マルチパート用キャッシュディレクトリを作成する

マルチパートアップロードの際、分割されたファイルを一時的に置く
ディレクトリを用意する。

```
sudo mkdir -p $CACHE_BASEDIR
sudo chmod 1777 $CACHE_BASEDIR
```

Gfarm 側に結合しながらアップロード後、一時ファイルは削除される。

##### ユーザを登録する

ユーザ登録にはglobal username、local username, S3用 access key ID の
3つ組情報が必要となる。

global username は Gfarm利用者のID、
local username はGfarm S3を動かすホストでの上記ユーザのログインIDである。
access key IDは本システム専用のIDとなる。

以下の例は、global username が user0001、
local username が localuser1、
access key ID としてはs3accesskeyidを指定したものである。

```
sudo $GFARM_S3_PREFIX/bin/gfarm-s3-useradd user0001 localuser1 s3accesskeyid
sudo usermod -a -G gfarms3 localuser1
```

##### httpdの設定を修正する
###### httpdを停止
```
sudo apachectl stop
```

###### apache-gfarm-s3.confの内容を、Apache設定の適切な場所に追加

上記Apache設定例の場合は、
configure 時に生成された
$WORKDIR/gfarm-s3-minio-web/etc/apache-gfarm-s3.conf
を$HTTPD_COMMON_CONFに追記する。

###### 403 error message file を配備する
```
cp $WORKDIR/gfarm-s3-minio-web/etc/e403.html $HTTPD_DocumentRoot/e403.html
```

###### メインインデックスにWebUIへのリンクを追加

WebUIにアクセスするには、/gfarm/console にブラウザでアクセスする。
以下はそのためのリンクを作成する設定例。

```
echo '<a href="/gfarm/console">gfarm-s3</a>' |
sudo sh -c "cat >> $HTTPD_DocumentRoot/index.html"
```
(URLパス名をgfarm以外に変更するには、
 $WORKDIR/gfarm-s3-minio-web/web/gfarm-s3/gfarms3/urls.py
 の``gfarm''も変更する。
    path('gfarm/console/', include('console.urls')),
)

###### httpdを起動
```
sudo apachectl start
```

##### serviceを登録・起動する
```
sudo systemctl enable --now gfarm-s3-webui.service
sudo systemctl enable --now gfarm-s3-router.service
```

##### 作業ディレクトリのcleanup
```
(cd $WORKDIR/gfarm-s3-minio-web && sudo make clean)
(cd $WORKDIR/gfarm-s3-minio-web && sudo make distclean)
```

以降、入手したソースコード、作業ディレクトリを削除してもOK

#### ユーザ(user0001)用のパスワードを表示する
パスワードの表示は、local user (localuser1) 権限で
gfarm-s3-sharedsecret-passwordを実行する。
WebUIにアクセスし、global username (user0001)と、このパスワードでログインする。
myproxy-logon, grid-proxy-init の場合には代理証明書のパスワードでログインする。

```
sudo -u localuser1 $GFARM_S3_PREFIX/bin/gfarm-s3-sharedsecret-password
```

##### Gfarmファイルシステム上に必要なディレクトリを作成する

Gfarm S3を使用するために、各ユーザに必要なディレクトリ
$SHARED_DIR/global-username を作成する。

$SHARED_DIRは「準備」セクションで決定したディレクトリである。
上記の例で追加した user0001 というユーザ名のディレクトリを作るには、以
下のように実行する。

```
gfsudo gfmkdir -p "${SHARED_DIR}"
gfsudo gfchmod 0755 "${SHARED_DIR}"

gfsudo gfmkdir "${SHARED_DIR}/user0001"
gfsudo gfchown user0001 "${SHARED_DIR}/user0001"
```

上記の操作をGfarm管理者(gfsudo実行可能)に依頼して実行する。

全GfarmユーザのGfarm S3用ディレクトリを作る場合の実行例:

```
SHARED_DIR=/share
gfsudo gfmkdir -p "${SHARED_DIR}"
gfsudo gfchmod 0755 "${SHARED_DIR}"

for u in $(gfuser); do
  NAME="$SHARED_DIR/$u"
  gfsudo gfmkdir -p "$NAME"
  gfsudo gfchmod 0755 "$NAME"
  gfsudo gfchown $u:gfarmadm "$NAME"
done
```

以上
