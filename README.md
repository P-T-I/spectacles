# spectacles
Gui for docker hub registry



create keys:


openssl req -newkey rsa:4096 -nodes -keyout domain.key -out domain.csr -subj "/C=NL/ST=NB/L=TILBURG/O=Docker Registry/CN=example.docker.reg"

Create a self-signed cert,

openssl x509 -signkey domain.key -in domain.csr -req -days 3650 -out domain.crt

