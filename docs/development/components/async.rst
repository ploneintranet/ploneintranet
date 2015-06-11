==========================
Asynchronous Functionality
==========================

Plone Intranet offers asynchronous task functionality
to offer a rich, responsive user experience.
For example document previews are generated and rendered without a browser refresh
and user notifications arrive in the browser without user interaction.

Architecture
============

Document preview example
------------------------

* Jane logs into the Intranet.
* Her browser attempts to open a websocket connection to a Tornado Websocket server.
* The Tornado server authenticates the socket open request against Plone using Jane's __ac cookie.
* Jane uploads a document to a workspace.
* Plone Intranet handles the object created event, and adds a docconv task to the queue passing Jane's __ac cookie
* Celery makes an HTTP request to the Plone Worker instance as Jane by using her cookie
* Plone Worker instance converts document/generates preview
* Plone Worker instance adds a "done" message to the queue
* Tornado server publishes "done" message to Jane's browser together with URL to fetch HTML snippet from
* Browser receives message from websocket with URL, makes AJAX request (using Patternslib) to fetch HTML and inject

The injected snippet would be the preview image.
This may be injected in multiple places.
For example on a content listing page, in an activity stream.
The destination IDs for pat-inject should be globally unique across the site.

Technology stack
----------------

* Tornado will provide a simple websocket server that authenticates against Plone
* Redis will provide message queues
* Celery will provide a simple worker to consume tasks from Redis and perform HTTP requests to Plone Worker instances
* A non web facing Plone instance will provide document conversion and preview generation

As we are using Celery, the message queue can be swapped out per deployment.


pat-inject-async
----------------

See `https://github.com/ploneintranet/ploneintranet.prototype/issues/75`

Previews that have been generated asynchronously
get pushed back into the DOM without requiring a refresh of the user's browser.

To do this we generate a HTML snippet of the preview
which contains the source and target attributes for pat-inject.
This snippet is sent to the browser over a websocket (described above).
pat-inject-async attaches an event handler to on_message event of SockJS

Development setup
-----------------

The default buildout sets up Celery in ALWAYS_EAGER mode.
This means you do not need to run the Celery worker or the broker (redis).

For development and testing this set up is ideal (preview generation will run synchronously for example)
but in production/staging you should follow the instruction below to set up a full async stack

Docsplit
~~~~~~~~

Docsplit is a 3rd party Ruby executable that provides preview generation of documents

See instructions at https://documentcloud.github.io/docsplit/

Production/Staging setup
------------------------

In order to deploy Plone Intranet to a staging/testing or production environment
you will need to do the following:

* Ensure the buildout config you are using overrides CELERY_ALWAYS_EAGER environment variable to be false
* Your supervisor (or other process management) config starts the Celery work (see below)
* Redis is installed and running as a system service (do not run redis under supervisor for security reasons)

Celery worker
~~~~~~~~~~~~~

In order for async to work, you need to have a celery worker running.
To start it run::

  $ bin/celery -A ploneintranet.async.celerytasks worker

