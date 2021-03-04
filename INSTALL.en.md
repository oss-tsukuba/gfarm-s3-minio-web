# Gfarm S3


## 1. Overview

Gfarm S3 is a S3 compatible object server for Gfarm.

Gfarm-S3 consists of S3 compatible server (MinIO),
reverse proxy (Apache),
wsgi server (gunicorn),
and WebUI framework (Django).

NOTE: nginx is not supported

NOTE: Apache comes with Centos7 does not support AF_UNIX communication to wsgi.
In this document, the communication configuration that uses AF_INET is
described.

### 1.1 Quick Installation

Though the Gfarm-S3 installation procedure is complicated 
for Gfarm-S3 depends on non-standard software,
the following procedure will do for most environment.

[IMPORTANT NOTE] Gfarm S3 requires Gfarm 2.7 (or later).
The system administrator privileges (root) and
Gfarm administrator (gfarmadm) privileges are required.

##### Choose working directory
(feel free to remove working directory after installation procedure finished)

```
export WORK=$HOME/tmp
mkdir -p $WORK
export MINIO_BUILDDIR=$HOME/tmp
mkdir -p $MINIO_BUILDDIR/minio/work/build
```

#### Obtain source code

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

#### Preparation

##### Choose parameters
```
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
```

##### Install prerequisites
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

##### Site settings (Apache)

skip this section if apache is already installed and configured properly.

###### Deploy apache http server

```
HTTPD_CONF=/etc/httpd/conf.d/myserver.conf
HTTPD_DocumentRoot=/usr/local/share/www
```

###### Site settings for apache
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

###### Generate main index of the site
```
sudo mkdir -p $HTTPD_DocumentRoot
echo "gfarm -- $(date)" | sudo dd of=$HTTPD_DocumentRoot/index.html
```

###### Enable httpd
```
sudo systemctl enable httpd
```

##### Create user and group for wsgi
```
sudo groupadd $WSGI_GROUP
id $WSGI_USER || sudo useradd $WSGI_USER -g $WSGI_GROUP -d $WSGI_HOMEDIR
```

#### Install gfarm-s3

##### Run configure in Gfarm-S3 source code

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

##### Install go
```
(cd $WORK/gfarm-s3-minio-web/minio && make install-go)
```

##### Build Gfarm-S3
```
(cd $WORK/gfarm-s3-minio-web && make)
```

##### Install Gfarm-S3
```
(cd $WORK/gfarm-s3-minio-web && sudo make install)
```

#### Gfarm-s3-settings

##### Create cache directory
```
sudo mkdir -p $CACHE_BASEDIR
sudo chmod 1777 $CACHE_BASEDIR
```

##### Register users

To register a user, global username, local username, S3access key ID,
of a user is used.

Here, global username is a user's Gfarm user ID,
local username is the user's login ID for the Gfarm S3 host system.
Access key ID is dedicated to Gfarm S3 system.

The following is an example that
global username is user0001,
local username is localuser1,
and access key ID is s3accesskeyid.

```
sudo $GFARM_S3_PREFIX/bin/gfarm-s3-useradd user0001 localuser1 s3accesskeyid
sudo usermod -a -G gfarms3 localuser1
```

##### Fix httpd.conf

###### Stop httpd
```
sudo apachectl stop
```

###### Add following file content to httpd.conf
```
sudo vi $WORK/gfarm-s3-minio-web/etc/apache-gfarm-s3.conf $HTTPD_CONF
```

###### deploy 403 error message file
```
cp $WORK/gfarm-s3-minio-web/etc/e403.html $HTTPD_DocumentRoot/e403.html
```

###### Add link to index page
```
echo '<a href="/gfarm/console">gfarm-s3</a>' |
sudo sh -c "cat >> $HTTPD_DocumentRoot/index.html"
```
(to change ``gfarm'' to another name, fix following definition in $WORK/gfarm-s3-minio-web/web/gfarm-s3/gfarms3/urls.py also:
    path('gfarm/console/', include('console.urls')),
)

###### Start httpd
```
sudo apachectl start
```

##### Start gunicorn service
```
sudo systemctl enable --now gunicorn.service
```

##### Cleanup
```
(cd $WORK/gfarm-s3-minio-web && sudo make clean)
(cd $WORK/gfarm-s3-minio-web && sudo make distclean)
```

#### Show sharedsecret password
To show a user's password, run gfarm-s3-sharedsecret-password as 
a corresponding local user (localuser1).
To login WebUI, use global username (user0001) and the password.
For myproxy-logon and grid-proxy-init , use proxy certificate's password.

```
sudo -u localuser1 $GFARM_S3_PREFIX/bin/gfarm-s3-sharedsecret-password
```

Access WebUI using global user id (user0001) and password showen by above command.



##### Create shared directory on Gfarm filesystem
The following procedure shall be performed by Gfarm Administrator.

Create $SHARED_DIR and $SHARED_DIR/global-username on Gfarm.

Here, $SHARE_DIR is the directory which decided in "prepare" section.

For example, registration info for user0001 (in above example) looks
like following:

```
gfsudo gfmkdir -p ${SHARED_DIR#/}
gfsudo gfchmod 1777 ${SHARED_DIR#/}

gfsudo gfmkdir ${SHARED_DIR#/}/user0001
gfsudo gfchown user0001 ${SHARED_DIR#/}/user0001
```

Ask Gfarm administrator to do above operation.

enjoy.
