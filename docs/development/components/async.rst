==========================
Asynchronous Functionality
==========================

The async package aims to facilitate a rich, responsive user experience
by offloading long running tasks to a worker instance of Plone.

For example document previews are generated
when new documents are uploaded.
This happens asynchronously to free up the user's browser for other tasks.
and user notifications arrive in the browser without user interaction.

Overview
========

Features
--------

* Buildout configuration to deploy Celery
* Previews API for generation and retrieval of preview images
* Tasks are performed synchronously by default, with an environment variable required to switch behaviour

Goals
-----

The main goal of this package is to provide a simple, well documented approach
to performing asynchronous tasks in Plone Intranet
that can be built upon as later asynchronous tasks are required

Implementation
--------------

Async is provided by `Celery`_. Celery is a proven, pure python, distributed task queue.
Tasks that are required to be asynchronous are added to the :mod:`celerytasks <ploneintranet.async.celerytasks>` module.
The Celery worker loads these tasks on start up and listens to the message queue
for calls to these tasks.

By default message queuing is to be provided by `Redis`_
For security reasons, we recommend this be installed as a system service so as to be maintained by sysadmin,
rather than adding it to buildout where it risks not having security patching performed.

The intention is for these Celery tasks to call back to Plone via HTTP requests
This provides several benefits:

* Ensures asynchronous jobs can still be performed as if the original user had initiated them
* Makes it easier to debug any issues as the tasks themselves are just HTTP requests
* Removes the need to give Celery access to the ZODB directly

For an example of this see :mod:`ploneintranet.async.celerytasks`

.. _Redis: http://redis.io
.. _Celery: http://www.celeryproject.org/

Preview Generation
==================

The primary requirement for async in the Plone Intranet project
is for generation of document preview images.

To make this simpler to use throughout the codebase,
we added previews to the Plone Intranet API :mod:`ploneintranet.api.previews`.
This provides a simple set of API calls to generate and fetch previews.
These are created when a user uploads files to the site.

There is an event subscriber for :class:`IObjectAddedEvent <zope.lifecycleevent.interfaces.IObjectAddedEvent>`
which simply calls the :function:`generate_and_add_preview <ploneintranet.async.celerytasks.generate_and_add_preview>` Celery task,
which in turn calls back to Plone via an HTTP request to perform the preview generation.
This is done by the :class:`GeneratePreviewImages <ploneintranet.async.browser.docconv.GeneratePreviewImages>` browser view
which calls the `Docsplit`_ binary as a subprocess.
This would normally be a blocking call, which is why we're doing asynchronously.

Currently this is as far as preview generation goes,
however `future iterations`_ of this will involve pushing the gnerated previews into the users browser via websockets

.. _Docsplit: https://documentcloud.github.io/docsplit/

Future iterations
=================

Final goal
----------

* Jane logs into the Intranet.
* Her browser attempts to open a websocket connection to a Tornado Websocket server.
* The Tornado server authenticates the socket open request against Plone using Jane's __ac cookie.
* Jane uploads a document to a workspace.
* Plone Intranet handles the object created event, and adds a docconv task to the queue passing Jane's __ac cookie
* Celery makes an HTTP request to the Plone Worker instance as Jane by using her cookie
* Plone Worker instance converts document/generates preview
* Plone Worker instance adds a "done" message to the queue
* Tornado server publishes "done" message to Jane's browser together with URL to fetch HTML snippet from
* Browser receives an HTML snippet from the websocket marked up with `pat-push`_

Technology stack
----------------

* Tornado will provide a simple websocket server that authenticates against Plone
* Redis will provide message queues
* Celery will provide a simple worker to consume tasks from Redis and perform HTTP requests to Plone Worker instances
* A non web facing Plone instance will provide document conversion and preview generation

As we are using Celery, the message queue can be swapped out per deployment.

pat-push
--------

See `https://github.com/ploneintranet/ploneintranet.prototype/issues/75`

Previews that have been generated asynchronously
get pushed back into the DOM without requiring a refresh of the user's browser.

To do this we generate a HTML snippet of the preview
which contains the source and target attributes for pat-inject.
This snippet is sent to the browser over a websocket (described above).
pat-inject-async attaches an event handler to on_message event of SockJS

Development setup
=================

The default buildout sets up Celery in ALWAYS_EAGER mode.
This means you do not need to run the Celery worker or the broker (redis).

For development and testing this set up is ideal (preview generation will run synchronously for example)
but in production/staging you should follow the instruction below to set up a full async stack

Production/Staging setup
========================

In order to deploy Plone Intranet to a staging/testing or production environment
you will need to do the following:

* Ensure the buildout config you are using overrides CELERY_ALWAYS_EAGER environment variable to be false
* Your supervisor (or other process management) config starts the Celery worker (see below)
* Redis is installed and running as a system service (do not run redis under supervisor for security reasons)

Celery worker
-------------

In order for async to work, you need to have a celery worker running.
To start it run::

  $ bin/celery -A ploneintranet.async.celerytasks worker

