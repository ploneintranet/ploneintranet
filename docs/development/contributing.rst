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

* The `project manager <mailto:info@ploneintranet.org>`_


.. note::

    If you're a Plone Intranet developer but not on the developer list, please subscribe at
    https://groups.io/org/groupsio/ploneintranet-dev


Open Source License
===================

This package is Copyright (c) Plone Foundation.

Any contribution to this package implies consent and intent to irrevocably transfer all 
copyrights on the code you contribute, to the `Plone Foundation`_, 
under the condition that the code remains under a `OSI-approved license`_.

To contribute, you need to have signed a Plone Foundation `contributor agreement`_.
If you're `listed on Github`_ as a member of the Plone organization, you already signed.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License version 2
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
`GNU General Public License`_ for more details.

.. _Plone Foundation: https://plone.org/foundation
.. _OSI-approved license: http://opensource.org/licenses
.. _contributor agreement: https://plone.org/foundation/contributors-agreement
.. _listed on Github: https://github.com/orgs/plone/people
.. _GNU General Public License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html


Definition of Done
==================

In order for a pull request to be accepted
the following development and style guidelines must be adhered to:

 * The `continuous integration <http://jenkins.ploneintranet.net>`_ build must be passing
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
