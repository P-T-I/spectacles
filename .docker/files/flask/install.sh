#!/bin/bash

chown 1000:1000 -R /app/data/

mv /app/client_secrets_template.json /app/client_secrets.json

rm -rf /app/.docker