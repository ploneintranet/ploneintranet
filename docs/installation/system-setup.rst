============
System setup
============

Some system packages are needed for a basic installation of Quaive.

.. warning::

   Plone Intranet can run on very different environments.
   The following instructions may not fit your system or your usual setup.
   If you need help write to the `developer mailing list`_ or on the #ploneintranet IRC channel.

We maintain an exact description of these requirements in the form of a Ubuntu 14.04
based Dockerfile_, which you can use either to
(a) build a Docker container, or
(b) as a guide set up your system manually

You are welcome to adapt them to your system and contribute your experience back to `our open source repository`_


(a) Docker-based OS setup
~~~~~~~~~~~~~~~~~~~~~~~~~

This requires `docker` to be available, see the `Docker installation docs`_.

Build a Docker container with the supplied Plone Intranet environment::

 docker build -t gaia .

Now startup and enter the docker container::

 docker run -i -t \
         --net=host \
         -e LC_ALL=en_US.UTF-8 \
         -e LANG=en_US.UTF-8 \
         -v $(PWD):/app -w /app -u app $(PROJECT)

The supplied `Makefile` provides a more advanced `docker-run` target
that mounts various extra directories and files into the container,
so you can re-use a global eggs cache in `/var/tmp/` etc. YMMV.


(b) Manual OS preparation
~~~~~~~~~~~~~~~~~~~~~~~~~

You can skip this section if you use the provided Dockerfile.

If you want to prepare your system environment manually, please use the Dockerfile_ as a reference.
That is, even if you don't use docker, see the documented `apt-get install` command there
for the list of packages you need to install in the operating system, before running buildout. YMMV.

Make sure you have the OS-level packages you need to build Plone, this can be
achieved using `install.plone.dependencies`_.

In addition, for the Plone Intranet file preview functionality, you need docsplit.

You will need some other tools installed for docsplit.
See the `docsplit installation instructions`_.
Note that Libre Office is mentioned as optional there, but in Plone Intranet we require it.

Solr is a required component. This will be built using buildout, but requires Java to be available.
On Ubuntu this normally comes pre-installed with the base OS.

Redis is a required component. This is *not* built with buildout, but expected to be available as a system service.
To install it on Ubuntu::

   sudo apt-get install redis-server

The default buildout is ldap-prepared. To make installing `python-ldap` possible, on Ubuntu you need::

   sudo apt-get install libldap2-dev libsasl2-dev

Ldap support is prepared, but disabled by default.
Please read the documentation section :doc:`ldap`
for instructions on installing and configuring LDAP.

On Ubuntu 16.04.2 LTS you can get the basic packages installed by running the following commands as root::

 apt-get update && apt-get install -y \
     cron \
     curl \
     file \
     firefox \
     gcc \
     gettext \
     ghostscript \
     git-core \
     graphicsmagick \
     jed \
     libenchant-dev \
     libffi-dev \
     libfreetype6-dev \
     libjpeg-dev \
     libldap2-dev \
     libreoffice \
     libsasl2-dev \
     libsqlite3-dev \
     libxslt1-dev \
     make \
     pdftk \
     poppler-data \
     poppler-utils \
     python-dev \
     python-gdbm \
     python-lxml \
     python-pip \
     python-tk \
     python-virtualenv \
     redis-server \
     ruby2.3 \
     ruby2.3-dev \
     wget \
     wv \
     xvfb \
     zlib1g-dev

  gem install docsplit

  locale-gen en_US.UTF-8 nl_NL@euro


.. _developer mailing list: https://groups.io/g/ploneintranet-dev
.. _our open source repository: https://github.com/ploneintranet/ploneintranet
.. _Docker installation docs: https://docs.docker.com/installation/
.. _Dockerfile: https://github.com/quaive/ploneintranet-docker-base/blob/master/Dockerfile
.. _install.plone.dependencies: https://github.com/collective/install.plone.dependencies
.. _docsplit installation instructions: https://documentcloud.github.io/docsplit/
