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

As mentioned in the previous paragraph spectacles needs 2 containers in order to be fully functional; 1 for the webserver
and 1 for a background process. The webserver container is the default with which the image is build and handles all
gui related actions and inputs. The background container is responsible for periodically contacting the registry and
updating the repository tag entries in the database. In order to activate the background process the command for the
spectacles image need to be overwritten with ``["manager.py", "runbackground"]``. As shown in the docker-compose_EXAMPLE.yml
file.

Environment variables
=====================

- ``DB_HOST`` (default: *mysql*): IP-address or FQDN of the MYSQL database;
- ``DB_BACKEND`` (default: *mysql*): Select which backend you would like to use for spectacles. Choices are 'mysql' or
  'other';
- ``SQLALCHEMY_DATABASE_URI`` (default: *sqlite:////app/data/db/spectacles.db*):

Configuring registry
--------------------

create keys:


openssl req -newkey rsa:4096 -nodes -keyout domain.key -out domain.csr -subj "/C=NL/ST=NB/L=TILBURG/O=Docker Registry/CN=example.docker.reg"

Create a self-signed cert,

openssl x509 -signkey domain.key -in domain.csr -req -days 3650 -out domain.crt

