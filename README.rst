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

Spectacles is a docker image which can be used to act as an authorization server for docker v2 registries. It provides
a web interface to allow you full control over the available repositories in your private registry. Spectacles has a
fine grained user management system and allows these user READ, WRITE or FULL access to repositories via the use of
fully configurable namespaces.

Database support
----------------
Spectacles can be used with different sql databases and has been tested with sqllite and mysql as database backends.
In order to fully make use of the functionalities of spectacles; an external mysql instance is highly advised.

This is because a local sqllite database will (for the moment) limit spectacles ability to fetch updates from the
registry via a (second spectacles instance) background process and fully persist spectacles state.
See `Configuring spectacles`_ for more details.

Configuring spectacles
----------------------

Gui for docker hub registry


Configuring registry
--------------------

create keys:


openssl req -newkey rsa:4096 -nodes -keyout domain.key -out domain.csr -subj "/C=NL/ST=NB/L=TILBURG/O=Docker Registry/CN=example.docker.reg"

Create a self-signed cert,

openssl x509 -signkey domain.key -in domain.csr -req -days 3650 -out domain.crt

