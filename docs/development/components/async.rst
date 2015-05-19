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
* A simple worker makes an HTTP request to the Plone Worker instance as Jane by using her cookie
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
* RQ (Redis Queue) will provide a simple worker to consume tasks from Redis and perform HTTP requests to Plone Worker instances
* A non web facing Plone instance will provide document conversion and preview generation
