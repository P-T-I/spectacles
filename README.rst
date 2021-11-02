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

Data Persistence
================

All data that should be able to survive a container rebuild/restart (like avatars, logs, registry certs, and sqllite
database) is saved by spectacles in the `/app/data` folder inside the container. So a volume should be mounted from
the host to the `/app/data` folder. As shown in the docker-compose_EXAMPLE.yml file.

Setup TLS for spectacles webserver
==================================

By default spectacles will run a HTTP webserver; if you would like to use a HTTPS webserver then mount an additional
volume containing the key en certificate (in pem format) into the container and set the environment variables
``SPECTACLES_WEB_TLS_KEY_PATH`` and ``SPECTACLES_WEB_TLS_CERT_PATH`` accordingly.

Environment variables
=====================

- ``DB_HOST`` (default: *mysql*): IP-address or FQDN of the MYSQL database;
- ``DB_BACKEND`` (default: *mysql*): Select which backend you would like to use for spectacles. Choices are 'mysql' or
  'other';
- ``SQLALCHEMY_DATABASE_URI`` (default: *sqlite:////app/data/db/spectacles.db*): The database URI that should be used
  for the connection. Examples:

  - sqlite:////tmp/test.db
  - mysql://username:password@server/db

- ``AVATARS_SAVE_PATH`` (default: */app/data/avatars/*): Path where to store the avatars created for spectacles users;
- ``SPECTACLES_PRIV_KEY_PATH`` (default: */app/data/certs/domain.key*): Path to where the private key used by the
  registry to validate the created tokens from spectacles. This should be the same key that is created in the paragraph
  `Configuring registry`_ and set to the environment variable ``REGISTRY_HTTP_TLS_KEY`` of the docker registry image;
- ``SPECTACLES_ISSUER_NAME`` (default: *Auth service*): Name you wish to give to the spectacles instance. Should be set
  to the same value as the environment variable ``REGISTRY_AUTH_TOKEN_ISSUER`` of the docker registry image;
- ``SPECTACLES_BACKGROUND_UPDATE`` (default: *30*): Specify the interval for the background process in seconds. 30 in
  this example makes sure that the background process runs every 30 seconds;
- ``SPECTACLES_WEB_TLS_KEY_PATH`` (default: */app/certs/key.pem*): Path to the TLS key for the HTTPS webserver;
- ``SPECTACLES_WEB_TLS_CERT_PATH`` (default: */app/certs/cert.pem*): Path to the TLS certificate for the HTTPS webserver;
- ``OPENID_LOGIN`` (default: *False*): Whether to use an openid provider for logging into spectacles (NOT SUPPORTED YET);
- ``SQL_DEBUG_LOGGING`` (default: *False*): If enabled all queries to the database are logged for debug purposes;
- ``LOG_FILE_PATH`` (default: */app/data/log/*): Directory where to store the logging;
- ``LOG_FILE_NAME`` (default: *spectacles.log*): Filename of the logging;
- ``SYSLOG_ENABLE`` (default: *False*): Whether to enable logging to a syslog server;
- ``SYSLOG_SERVER`` (default: *172.16.1.1*): IP address or FQDN of the syslog server;
- ``SYSLOG_PORT`` (default: *5140*): UDP port of the syslog server;

Configuring registry
--------------------

The registry that can be used for spectacles is a normal `docker registry <https://hub.docker.com/_/registry>`_ and
further details and settings about that image is listed there.

However for simplicity sake here is an example of the environment settings that should be set on the image:
   - REGISTRY_STORAGE_DELETE_ENABLED=true
   - REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY=/mnt/registry/data
   - REGISTRY_AUTH=token
   - REGISTRY_AUTH_TOKEN_REALM=https://localhost:5050/token_auth
   - REGISTRY_AUTH_TOKEN_SERVICE="Docker registry"
   - REGISTRY_AUTH_TOKEN_ISSUER="Auth service"
   - REGISTRY_AUTH_TOKEN_ROOTCERTBUNDLE=/mnt/local/certs/domain.crt
   - REGISTRY_HTTP_TLS_CERTIFICATE=/mnt/local/certs/domain.crt
   - REGISTRY_HTTP_TLS_KEY=/mnt/local/certs/domain.key

Couple of pointers:

- the ``REGISTRY_STORAGE_DELETE_ENABLED`` variable controls whether or not the registry let's you 'delete' a
  repository / tag.
  Please keep in mind that, although the repository / tag seems deleted, it's not really gone until you run the registry's
  garbage collector. More details in the `documentation <https://docs.docker.com/registry/>`_;
- the ``REGISTRY_AUTH_TOKEN_REALM`` should be set to the IP address / FQDN of the spectacles webserver and should point
  to the token_auth endpoint;
- the ``REGISTRY_AUTH_TOKEN_ISSUER`` should be set to the same value as ``SPECTACLES_ISSUER_NAME`` from the previous
  paragraph;
- the ``REGISTRY_HTTP_TLS_KEY`` should be set to the path to the registry's private key and should be set to the same
  key as ``SPECTACLES_PRIV_KEY_PATH``. The private key can be created via the command:

   openssl req -newkey rsa:4096 -nodes -keyout domain.key -out domain.csr -subj "/C=XX/ST=XX/L=XXXX/O=Docker
   Registry/CN=example.docker.reg"

- the ``REGISTRY_AUTH_TOKEN_ROOTCERTBUNDLE`` and the ``REGISTRY_HTTP_TLS_CERTIFICATE`` should be set to the path of the
  registry's signed certificate. The certificate can be created / signed via the command:

   openssl x509 -signkey domain.key -in domain.csr -req -days 3650 -out domain.crt

- if you would like to persist the registry's data you should mount a volume to the /mnt/registry/data;
- the certificate and key created earlier should be mounted into the /mnt/local/certs.

Quick start
-----------

The easiest way to quickly setup a full suite is to use the provided docker-compose_EXAMPLE.yml. Once that file is
tweaked to your specifications all steps below assume that you've renamed the docker-compose_EXAMPLE.yml to
docker-compose.yml; if that's not the case you should specify the file with a -f flag appended to the docker-compose
command.

These steps can be read in the full `documentation <https://p-t-i.github.io/spectacles/>`_ (NOT COMPLETED YET);

Start all containers:

   docker-compose up

Once the containers are up and running; navigate to http(s)://localhost:5050 and register your first user. (The first
registered user will automatically be made an administrative user.)

Once logged-in navigate to the 'Registries' page and add your first registry.

Once successful add a namespace to the registry you've just configured by navigating to the namespaces page and create
the namespace 'test'.

Now your set to login to your registry and push your first repository.

From the command line (assuming your registry runs on the default port of 5000):

   docker login localhost:5000

It will request your username and password (from the admin user you've just created within spectacles) and will report
back when the login is successful.

Now pull a image from the public docker hub and tag it for our private repository:

   docker pull hello-world
   docker tag hello-world:latest localhost:5000/test/hello-world:latest

Push the image to the private repo:

   docker push localhost:5000/test/hello-world:latest

Once the sheduled background process has completed it will show up within spectacles.
