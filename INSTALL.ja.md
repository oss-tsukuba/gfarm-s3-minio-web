# Gfarm S3 インストール手順書

## 1. Overview

Gfarm S3 is a S3 compatible object server for Gfarm.

Gfarm S3は、以下のコンポーネントから構成される

* S3 互換サーバ (MinIO),
* リバースプロキシ (Apache),
* wsgi サーバ (gunicorn),
* WebUI フレームワーク (Django).

※ nginxはサポートされてません

※ wsgiの設定について: Centos7標準のApacheではwsgiとの通信にAF_UNIXが
使用できないため、本文書ではAF_INETを使用する手順を示しています

インストール手順は、以下のとおり

0. 事前準備
  * 依存パッケージのインストール
  * Apacheのインストール
  * WebUIフレームワークを動作させるユーザを作成

1. Gfarm S3のソースコードから以下のコンポーネントをインストール
  * WebUI フレームワーク (Django)
  * S3 互換サーバ (MinIO)
  * gunicorn用のsystemdファイル

2. ApacheにGfarm S3用の設定を追加

3. guniconサービスを起動


### 1.1 Quick Installation

本節ではインストール手順を簡単に説明する
本手順はCentos7およびCentos8で動作確認している

【重要】インストールは、Gfarm 2.7 (以降) がインストール
されている環境で行う。ホストの管理権限 (root) および
Gfarmの管理者権限 (gfarmadm) が必要となる。

##### Gfarm-S3をビルドするための作業ディレクトリを作成
(インストール後は削除して構わないのでどこでもよい)

```
export WORK=$HOME/tmp
mkdir -p $WORK
export MINIO_BUILDDIR=$HOME/tmp
mkdir -p $MINIO_BUILDDIR/minio/work/build
```

#### Gfarm S3のソースコードを入手する

```
(cd $WORK &&
 git clone git@github.com:oss-tsukuba/gfarm-s3-minio-web.git)
(cd $WORK/gfarm-s3-minio-web &&
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
GFARM_S3_PREFIX=/usr/local      # Gfarm-S3をインストールする場所
SHARED_DIR=/share               # Gfarm上のGfarm-S3に使用するディレクトリ
CACHE_BASEDIR=/mnt/cache        # キャッシュ用ディレクトリ
CACHE_SIZE=1024                 # 1ユーザあたりのキャッシュサイズ(MB)
WSGI_USER=wsgi                  # wsgiを動かすユーザID
WSGI_GROUP=wsgi                 # 同グループ
WSGI_HOMEDIR=/home/wsgi         # 同ホームディレクトリ
WSGI_PORT=8000                  # 同待ち受けポート
MYPROXY_SERVER=                 # myproxy-logonを使用するば場合はサーバを指定する
```

##### 依存パッケージをインストールする

```
sudo yum update -y
sudo yum install -y httpd mod_ssl uuid myproxy \
         python3-devel python3-pip nodejs 
```

```
sudo python3 -m pip install 'Django<2.2'
sudo python3 -m pip install gunicorn
sudo python3 -m pip install boto3
```

##### Apacheを設定する

既にインストールされていれば本作業は不要

###### Apacheのインストール場所を決める
```
HTTPD_CONF=/etc/httpd/conf.d/myserver.conf
HTTPD_DocumentRoot=/usr/local/share/www
```

###### Apacheの設定ファイルを作成
```
cat <<EOF | sudo dd of=$HTTPD_CONF
ServerName ${GFDOCKER_SUBNET%.0/24}.$GFDOCKER_START_HOST_ADDR
<VirtualHost *:443>
	SSLEngine on
	SSLCertificateFile /etc/pki/tls/certs/localhost.crt
	SSLCertificateKeyFile /etc/pki/tls/private/localhost.key
	DocumentRoot $HTTPD_DocumentRoot
	ServerAdmin root@localhost
	CustomLog logs/access_log common
	ErrorLog logs/error_log

	<Directory "$HTTPD_DocumentRoot">
		AllowOverride FileInfo AuthConfig Limit Indexes
		Options MultiViews Indexes SymLinksIfOwnerMatch Includes
		AllowOverride All
		Require all granted
	</Directory>

</VirtualHost>
EOF
```

###### Apacheのメインインデックスを作成
```
sudo mkdir -p $HTTPD_DocumentRoot
echo "gfarm -- $(date)" | sudo dd of=$HTTPD_DocumentRoot/index.html
```

###### Apacheを有効化する
```
sudo systemctl enable httpd
```

##### wsgi用のグループとユーザを作成する
```
sudo groupadd $WSGI_GROUP
id $WSGI_USER || sudo useradd $WSGI_USER -g $WSGI_GROUP -d $WSGI_HOMEDIR
```

#### install gfarm-s3

##### 作業ディレクトリに移動し configure

パラメータは上で決定したものを使用
with-gfarm, with-globus, with-myproxy, 
with-apache, with-gunicornはそれぞれのインストール
プレフィックスを指定する。

```
(cd $WORK/gfarm-s3-minio-web && ./configure \
	--prefix=$GFARM_S3_PREFIX \
	--with-gfarm=/usr/local \
	--with-globus=/usr \
	--with-myproxy=/usr \
	--with-apache=/usr \
	--with-gunicorn=/usr/local \
	--with-wsgi-homedir=$WSGI_HOMEDIR \
	--with-wsgi-user=$WSGI_USER \
	--with-wsgi-group=$WSGI_GROUP \
	--with-wsgi-port=$WSGI_PORT \
	--with-cache-basedir=$CACHE_BASEDIR \
	--with-cache-size=$CACHE_SIZE \
	--with-myproxy-server=$MYPROXY_SERVER \
	--with-gfarm-shared-dir=$SHARED_DIR \
	--with-minio-builddir=$MINIO_BUILDDIR)
```

##### Go を作業ディレクトリにインストールする
```
(cd $WORK/gfarm-s3-minio-web/minio && make install-go)
```

##### Gfarm-S3をビルドする
```
(cd $WORK/gfarm-s3-minio-web && make)
```

##### Gfarm-S3をインストールする
```
(cd $WORK/gfarm-s3-minio-web && sudo make install)
```

#### Gfarm-S3の設定

##### キャッシュディレクトリを作成する
```
sudo mkdir -p $CACHE_BASEDIR
sudo chmod 1777 $CACHE_BASEDIR
```

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

###### apache-gfarm-s3.confの内容を、httpd.confの適当な場所に追加する
以下は、上述の$HTTPD_CONFに追加する例
```
sudo vi $WORK/gfarm-s3-minio-web/etc/apache-gfarm-s3.conf $HTTPD_CONF
```

###### 403 error message file を配備する
```
cp $WORK/gfarm-s3-minio-web/etc/e403.html $HTTPD_DocumentRoot/e403.html
```

###### メインインデックスにWebUIへのリンクを追加
```
echo '<a href="/gfarm/console">gfarm-s3</a>' |
sudo sh -c "cat >> $HTTPD_DocumentRoot/index.html"
```
(gfarm以外にするには、 $WORK/gfarm-s3-minio-web/web/gfarm-s3/gfarms3/urls.py の``gfarm''も変更
    path('gfarm/console/', include('console.urls')),
)

###### httpdを起動
```
sudo apachectl start
```

##### gunicorn serviceを起動する
(gunicorn.serviceはGfarm-S3のmake installでコピーされている)
```
sudo systemctl enable --now gunicorn.service
```

##### cleanup
```
(cd $WORK/gfarm-s3-minio-web && sudo make clean)
(cd $WORK/gfarm-s3-minio-web && sudo make distclean)
```

以降、入手したソースコード、作業ディレクトリを削除してもOK

#### ユーザ(user0001)用のパスワードを表示する
パスワードの表示は、local user (localuser1) 権限で 
gfarm-s3-sharedsecret-passwordを実行する。
WebUIにアクセスし、global username (user0001)と、このパスワードでログインする
myproxy-logon, grid-proxy-init の場合には代理証明書のパスワードでログインする。


```
sudo -u localuser1 $GFARM_S3_PREFIX/bin/gfarm-s3-sharedsecret-password
```

##### Gfarmファイルシステム上に必要なディレクトリを作成する

Gfarm S3で共通に必要なディレクトリ $SHARED_DIR と、
各ユーザに必要なディレクトリ$SHARED_DIR/global-username を作成する。

ここに$SHARED_dirは「準備」セクションで決定したディレクトリである。
上記の例で追加した user0001 というユーザであれば、以下の例のようになる。

```
gfsudo gfmkdir -p ${SHARED_DIR#/}
gfsudo gfchmod 1777 ${SHARED_DIR#/}

gfsudo gfmkdir ${SHARED_DIR#/}/user0001
gfsudo gfchown user0001 ${SHARED_DIR#/}/user0001
```

上記の操作は、Gfarm管理者に依頼して実行する。

以上
