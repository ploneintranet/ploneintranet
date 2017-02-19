===========
User Manual
===========

Location
========

The Quaive User Manual, or "handbook", is maintained in a `separate repository`_ on github.

A publicly available version can be found at: http://manual.quaive.net/

The landing page ist just a switch for choosing the desired language. The contents of the user manual are available under their respective language abbreviation: http://manual.quaive.net/en, http://manual.quaive.net/de, etc

Contributing
============

Check out the repository on github. It contains instructions on how to build the manual locally.

All contents **must** be placed under one of the language folders. The main language is English. Feel free to add more translations...

Please try to keep the hierarchy of the docs as flat as possible. Not every reader will understand *your* preferred structure.

Updating the public version
===========================

The public version (http://manual.quaive.net/) is located on ext3.syslab.com. It is updated every 10 minutes based on the latest state of the master branch. Therefore, simply push your changes to master.

To manually update, `ssh` to the server, become user "quaive", `cd /home/quaive/quaive.manual` and run the upgrade.

If you need access to the server, contact Wolfgang (pysailor).


.. _separate repository: https://github.com/quaive/quaive.manual