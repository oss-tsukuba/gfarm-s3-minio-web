# Settings

## Limit authentication method:

To limit authentication method of WebUI to one of
myproxy-logon, grid-proxy-init or, sharedsecret,
set appropriate value to `GFARMS3_LOGIN_METHOD` in
`/usr/local/etc/gfarm-s3.conf`.

Available value are following:

GFARMS3_LOGIN_METHOD=myproxy-logon,grid-proxy-init,gfarm-shared-key
GFARMS3_LOGIN_METHOD=myproxy-logon,grid-proxy-init
GFARMS3_LOGIN_METHOD=myproxy-logon,gfarm-shared-key
GFARMS3_LOGIN_METHOD=grid-proxy-init,gfarm-shared-key
GFARMS3_LOGIN_METHOD=myproxy-logon
GFARMS3_LOGIN_METHOD=grid-proxy-init
GFARMS3_LOGIN_METHOD=gfarm-shared-key

