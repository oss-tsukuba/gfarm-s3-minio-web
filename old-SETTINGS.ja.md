# 設定

## 認証方法の制限:

/usr/local/etc/gfarm-s3.confで設定されている
以下の変数を変更することで、WebUIで使用可能な認証方式を
myproxy-logon, grid-proxy-init, 共有鍵のいずれかに
限定することが可能。

指定可能な値は以下のとおり:

GFARMS3_LOGIN_METHOD=myproxy-logon,grid-proxy-init,gfarm-shared-key
GFARMS3_LOGIN_METHOD=myproxy-logon,grid-proxy-init
GFARMS3_LOGIN_METHOD=myproxy-logon,gfarm-shared-key
GFARMS3_LOGIN_METHOD=grid-proxy-init,gfarm-shared-key
GFARMS3_LOGIN_METHOD=myproxy-logon
GFARMS3_LOGIN_METHOD=grid-proxy-init
GFARMS3_LOGIN_METHOD=gfarm-shared-key
