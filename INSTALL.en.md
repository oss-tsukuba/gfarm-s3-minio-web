# Gfarm S3


## 1. Overview

Gfarm S3 is a S3 compatible object server for Gfarm.

Gfarm-S3 consists of S3 compatible server (MinIO),
reverse proxy (Apache),
wsgi server (gunicorn),
and WebUI framework (Django).


### 1.1 Quick Installation

Though the Gfarm-S3 installation procedure is complecated 
for Gfarm-S3 depends on non-standard software,
the following procedure will do for most environment.

[IMPORTANT NOTE] Gfarm S3 requires Gfarm 2.7 (or later).
The system administorate priviliege (root) and
Gfarm administrator (gfarmadm) privilege are required.

#### obtain source code

Decide where to put source code and get source code.
Let us assmme souce code will go GFARM_SE_MINIO_WEB_SRC and
GFARM_SE_MINIO_SRC.

``
GFARM_SE_MINIO_WEB_SRC=/tmp/work/gfarm-s3-minio-web
mkdir -p $(dirname $GFARM_SE_MINIO_WEB_SRC)
(cd $(dirname $GFARM_SE_MINIO_WEB_SRC) &&
 git clone git@github.com:oss-tsukuba/gfarm-s3-minio-web.git)
(cd $GFARM_SE_MINIO_WEB_SRC && git checkout develop)

GFARM_SE_MINIO_SRC=/tmp/work/gfarm-s3-minio
mkdir -p $(dirname $GFARM_SE_MINIO_SRC)
(cd $(dirname $GFARM_SE_MINIO_SRC) &&
 git clone git@github.com:oss-tsukuba/gfarm-s3-minio.git)
(cd $GFARM_SE_MINIO_SRC && git checkout gatewaygfarm)
``

#### preparation

##### choose parameters
``
GFARM_S3_PREFIX=/usr/local      # Gfarm-S3 install prefix
SHARED_DIR=/share               # S3 bucket rootdir on Gfarm
CACHE_BASEDIR=/mnt/cache        # cache directory for minio
CACHE_SIZE=1024                 # per user cache size (in MB)
WSGI_USER=wsgi                  # userid for wsgi process
WSGI_GROUP=wsgi                 # gropuid for wsgi process
WSGI_HOMEDIR=/home/wsgi         # user wsgi's home directory
WSGI_PORT=8000                  # wsgi port
			        # (AF_UNIX is not available)
MYPROXY_SERVER=                 # myporoxy server for myproxy-logon
``

##### install prerequisites
``
sudo yum update -y
sudo yum install -y httpd mod_ssl uuid myproxy \
         python3-devel python3-pip nodejs 
``

(nginx is not supported yet; sudo yum install -y nginx)

``
sudo python3 -m pip install 'Django<2.2'
sudo python3 -m pip install gunicorn
sudo python3 -m pip install boto3
``

##### site settings (Apache)

skip this section if apache is already installed and configured properly.

###### deploy apache http server

``
HTTPD_CONF=/etc/httpd/conf.d/myserver.conf
HTTPD_DocumentRoot=/usr/local/share/www
``

###### site settings for apache
``
cat <<EOF | sudo dd of=$HTTPD_CONF
ServerName ${GFDOCKER_SUBNET%.0/24}.$GFDOCKER_START_HOST_ADDR
<VirtualHost *:80>
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
``

###### genereate main index of the site
``
sudo mkdir -p $HTTPD_DocumentRoot
echo "gfarm -- $(date)" | sudo dd of=$HTTPD_DocumentRoot/index.html
``

###### enable httpd
``
sudo systemctl enable httpd
``

(nginx is not supported yet; vi /etc/nginx/nginx.conf; systemctl enable nginx.service)

##### create user and group for wsgi
``
sudo groupadd $WSGI_GROUP
id $WSGI_USER || sudo useradd $WSGI_USER -g $WSGI_GROUP -d $WSGI_HOMEDIR
``

#### install gfarm-s3

##### choose working directory
(feel free to remove working directory after installation procedure finished)

``
export WORK=$HOME/tmp/work
mkdir -p $WORK
export MINIO_BUILDDIR=$HOME/tmp/work
mkdir -p $MINIO_BUILDDIR
mkdir -p $MINIO_BUILDDIR/minio/work/build
``

##### copy source code into woking space
``
rsync -a $GFARM_SE_MINIO_WEB_SRC/ $WORK/gfarm-s3-minio-web/
rsync -a $GFARM_SE_MINIO_SRC/ $MINIO_BUILDDIR/minio/work/build/gfarm-s3-minio/
``

##### run configure in Gfarm-S3 source code

``
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
``

##### install go
``
(cd $WORK/gfarm-s3-minio-web/minio && make install-go)
``

##### build Gfarm-S3
``
(cd $WORK/gfarm-s3-minio-web && make)
``

##### install Gfarm-S3
``
(cd $WORK/gfarm-s3-minio-web && sudo make install)
``

#### gfarm-s3-settings

##### create cache directory
``
sudo mkdir -p $CACHE_BASEDIR
sudo chmod 1777 $CACHE_BASEDIR
``

##### register users

To register a user, global username, local username, S3access key ID,
of a user is used.

Here, global username is a user's Gfarm user ID,
local username is the user's login ID for the Gfarm S3 host system.
Access key ID is dedicated to Gfarm S3 system.

The following is an example that
global username is hpci0001,
local username is user1,
and access key ID is s3accesskeyid.

``
sudo $GFARM_S3_PREFIX/bin/gfarm-s3-useradd hpci0001 user1 s3accesskeyid
sudo usermod -a -G gfarms3 user1
``

##### fix httpd.conf

###### stop httpd
``
sudo apachectl stop
``

###### add following file content to httpd.conf
``
sudo vi $WORK/gfarm-s3-minio-web/etc/apache-gfarm-s3.conf $HTTPD_CONF
``

###### add link to index page
``
echo '<a href="/d/console">gfarm-s3</a>' |
sudo sh -c "cat >> $HTTPD_DocumentRoot/index.html"
``

###### start httpd
``
sudo apachectl start
``

##### start gunicorn service
``
sudo systemctl enable --now gunicorn.service
``

##### cleanup
``
(cd $WORK/gfarm-s3-minio-web && sudo make clean)
(cd $WORK/gfarm-s3-minio-web && sudo make distclean)
``

#### show sharedsecret password
``
sudo -u user1 $GFARM_S3_PREFIX/bin/gfarm-s3-sharedsecret-password
``

Access WebUI using user-id (user1) and password showen by above command.



##### create shared directory
The following procedure shall be performed by Gfarm Administrator.

Create $SHARED_DIR and $SHARED_DIR/global-username on Gfarm.

Here, $SHARE_DIR is the directory which decided in "prepare" section.

For example, registration info for hpci0001 (in above example) looks
like following:

``
gfsudo gfmkdir -p ${SHARED_DIR#/}
gfsudo gfchmod 1777 ${SHARED_DIR#/}

gfsudo gfmkdir ${SHARED_DIR#/}/hpci0001
gfsudo gfchown hpci0001 ${SHARED_DIR#/}/hpci0001
``

Ask Gfarm administrator to do above operation.

enjoy.
