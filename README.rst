.. image:: images/spectacles_text.png

.. Everything after the include marker below is inserted into the sphinx html docs. Everything above this comment is
   only visible in the github README.rst
   ##INCLUDE_MARKER##

.. image:: https://img.shields.io/github/release/P-T-I/spectacles.svg
   :target: https://GitHub.com/P-T-I/spectacles/releases/

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0

.. image:: https://badgen.net/badge/Github/repo/green?icon=github
   :target: https://GitHub.com/P-T-I/spectacles

spectacles
----------

Gui for docker hub registry



create keys:


openssl req -newkey rsa:4096 -nodes -keyout domain.key -out domain.csr -subj "/C=NL/ST=NB/L=TILBURG/O=Docker Registry/CN=example.docker.reg"

Create a self-signed cert,

openssl x509 -signkey domain.key -in domain.csr -req -days 3650 -out domain.crt

