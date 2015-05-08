==========================
Building the Documentation
==========================

System dependencies
-------------------

To build the documentation you need to have the `Enchant <http://www.abisource.com/projects/enchant/>`_ library installed on your system.
To install the Enchant library on Ubuntu::

    sudo apt-get install libenchant-dev

To install the Enchant library on OSX using brew.::

    brew install enchant

Alternatively see the `stackoverflow article`_ on Enchant and OSX.

Generating the documentation
----------------------------

The documentation is in the folder ``/docs``

The buildout creates a script in bin to generate the docs::

   bin/generate-docs

The docs are generated in docs/html.

.. _`stackoverflow article`: http://stackoverflow.com/questions/3683181/cannot-install-pyenchant-on-osx
