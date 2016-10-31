==================
Plone Intranet API
==================

The ``ploneintranet.api`` package provides a simple developer API to the most commonly used features of ploneintranet.

Disabling event handlers
------------------------

Sometimes, e.g. during a transmogrifier import, you want to disable certain
event handers, either because you don't want their autocreation effects,
or because they're computationally costly.

This becomes especially important because of the async nature of the costly
heavy lifting handlers. In case of a long-running original request (say,
a deep copy or a big import) the async job may fire *before* the original
request is completed. In that case, because the original request has not
yet committed, the async job has nothing to work on, which leads to rescheduling
of async jobs, a lot of log noise, and much developer head scratching.

So, just disable that stuff. Each of these has alternatives that can be used
for ex-post batch fixing:

- Solr indexing can be done post-hoc with the ``@@solr-maintenance`` view

- There's a subtree reindexing view too somewhere

- Preview generation can be done post-hoc via ``@@generate-previews-for-contents``
  and its async variant

- Microblog content updates can be created post-hoc by running the
  ``ploneintranet.microblog:default > discuss older docs`` upgrade step.

.. automodule:: ploneintranet.api.events
    :members:
    :undoc-members:
    :show-inheritance:


Microblogging API
-----------------

.. automodule:: ploneintranet.api.microblog.statusupdate
    :members:
    :undoc-members:
    :show-inheritance:

Previews API
------------

.. automodule:: ploneintranet.api.previews
    :members:
    :undoc-members:
    :show-inheritance:

User Profile API
----------------

.. automodule:: ploneintranet.api.userprofile
    :members:
    :undoc-members:
    :show-inheritance:

