==========================================
Contributing to the Plone Intranet Project
==========================================

.. admonition:: Description

   How to develop and submit code for the Plone Intranet Project.

.. contents:: :local:


Reaching the Plone Intranet team
================================

To reach the Plone Intranet development team for any questions please contact

* `Plone Intranet Developers mailing list <mailto:ploneintranet-dev@groups.io>`_

* *#plone.intranet* IRC channel on irc.freenode.net

License
=======

.. note::

   License goes here

Definition of Done
==================

In order for a pull request to be accepted
the following development and style guidelines must be adhered to:

 * The `continuous integration <http://jenkins.ploneintranet.net>`_ build must be
   passing
 * Any contributed code, must have 100% test coverage
 * Every contributed python function or method should have a test
 * Code that handles user input, must have unicode tests
 * Every UI form must have an associated robot test
 * Without exception, all contributed code must adhere to `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_
 * All contributed code must have docstrings
 * All contributed APIs must have full `Sphinx style docstrings <https://pythonhosted.org/an_example_pypi_project/sphinx.html>`_

   - Avoid committing code directly to master
   - Pull requests must be reviewed by at least one other developer working on the project
   - Assign pull requests to another developer so they get notified, and chase them to review it.
     Stagnant pull requests become a lot harder to merge later.

 * Keep README and CHANGES up to date
 * Don't commit commented-out code. We have version control, if you want to add code back later.
