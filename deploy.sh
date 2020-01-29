#! /usr/bin/env bash

apt update

apt install nginx redis-server git build-essential


INSTANCE="vurl"
USERNAME="vurl"
CONFIGPATH="/etc/${INSTANCE}"
CONFIGFILE="${CONFIGPATH}/${INSTANCE}.yml"
PYTHON=$(which python3.6)
PIP=$(which pip3.6)

useradd -r ${USERNAME}

$PIP install gunicorn
$PIP install .


mkdir -p $CONFIGPATH
echo "
debug: true
" > ${CONFIGFILE}


echo "d /run/${INSTANCE} 0755 ${USERNAME} ${USERNAME} -" > /etc/tmpfiles.d/${INSTANCE}.conf


echo "
import os
from vurlwebapi import app

app.settings.loadfile('${CONFIGFILE}')
app.ready()

" > ${CONFIGPATH}/wsgi.py


echo "
[Unit]
Description=vurl REST API
After=network.target

[Service]
PIDFile=/run/${INSTANCE}/pid
User=${USERNAME}
Group=${USERNAME}
ExecStart=/usr/local/bin/gunicorn --workers 1 --bind unix:/run/${INSTANCE}/${INSTANCE}.socket --pid /run/${INSTANCE}/pid --chdir ${CONFIGPATH} wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
ExecStop=/bin/kill -s TERM \$MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/${INSTANCE}.service

systemd-tmpfiles --create
systemctl daemon-reload
systemctl enable ${INSTANCE}.service
service ${INSTANCE} start


echo "
upstream ${INSTANCE}_api {
    server unix:/run/${INSTANCE}/${INSTANCE}.socket fail_timeout=1;
}


server {
    listen 443 ssl http2;

    location ~ ^/apiv1/(?<url>.*) {
      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_redirect off;
      proxy_pass http://${INSTANCE}_api/\$url;
    }
}
" > /etc/nginx/sites-available/${INSTANCE}.conf
ln -s /etc/nginx/sites-available/${INSTANCE}.conf /etc/nginx/sites-enabled/${INSTANCE}.conf
service nginx restart

