#!/bin/bash

mkdir -p /app/data/db
touch /app/data/db/spectacles.db

mkdir -p /app/data/avatars
mkdir -p /app/data/log

chown 1000:1000 -R /app/data/

mv /app/client_secrets_template.json /app/client_secrets.json

rm -rf /app/.docker