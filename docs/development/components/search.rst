======
Search
======

This package aims to provide a common API
for querying from Plone to 3rd party search engines e.g. Solr

Overview
========

Features
--------

* Thin API layer to support retrieval of search data (based on design prototypes of search interface)

* collective.indexing integration to automatically hook into Plone's catalog operations

* Integration with Plone Intranet UI providing faceting, spell-check, highlighting etc.

* Configurable options for filtering, faceting and boosting

Goals
-----

* Solr backend implementation providing better relevancy, spell checking and highlighting than ZCatalog can offer

* Possible Elasticsearch or other backend support in the future

Restrictions
------------

.. warning:: Solr is required

Initially, we had a goal of also shipping with ZCatalog support without hard requiring Solr.
This is still reflected in the code, which also offers a level of ZCatalog-only support.
However we've since discovered that maintaining ZCatalog-only support will not be possible.

Please always develop and deploy with the Solr backend enabled.
Our default buildout.cfg ships with Solr enabled.

Why not collective.solr?
------------------------

collective.solr_ has the noble goal of completely replacing Plone's catalog with a Solr_ backend in a seamless manner.
All search queries to Plone's catalog are intercepted and translated to the equivalent Solr queries.

Unfortunately the requirements for an accurate, intelligent and configurable site-wide search do not align well with this
approach, as the Plone catalog query API will always be a limitation to querying Solr. This makes it hard to
configure options such as per-content-type boosting, faceting and so on, as the Plone catalog has no concept of these features.

Some of the other key benefits of rolling our own solution are:

* No need for monkeypatching of core Plone code
* No need for legacy code to support old Plone versions
* Thin API layer removes the tight integration with Solr, allowing for other search
  backends to be added in future

ploneintranet.search owes a great debt to collective.solr and its authors, as many of the concepts and solutions 
we employ are borrowed from it.

.. _collective.solr: https://plone.org/products/collective.solr
.. _Solr: http://lucene.apache.org/solr/

Enabling the solr backend
=========================

If developing for Plone Intranet, you will need to run buildout using the separate solr buildout file. This will set up two solr instances (the second is reserved for integration tests).

.. code:: bash

  ./bin/buildout -c solr.cfg

The main solr instance can then be started using the utility script 'solr-start':

.. code:: bash

  ./bin/solr-start

If you are deploying Plone Intranet, you will need to use the solr.cfg buildout file as a reference for your own buildout setup, adapting it to change ports, directories and fields as necessary.

If moving an existing site to a SOLR backend, you will need to run the 'Clear and Rebuild' step on the portal_catalog, which will sync all items with the solr database. (This only needs to be done once.)


solr maintenance views
----------------------

Ploneintranet provides 2 solr maintenance views:

`@@solr-optimize`
  is a view you will want to call from cron at least once per day, to perform regular optimizations.

`@@solr-maintenance`
  does a full reindex of solr
  

Configuration
=============

Adding filters
--------------

To register a new filter:

1. Make sure the filter data is accessible on your content, either directly on a field/method or via plone.indexer_.
2. Update your solr schema to include the new field in Solr.
3. Include the filter in the `ploneintranet.search.filter_fields` registry entry as follows:

.. code:: xml

  <record name="ploneintranet.search.filter_fields">
    <field type="plone.registry.field.Tuple">
      <title>Filter fields</title>
      <description>Fields that will be used to filter query responses in searches</description>
      <value_type type="plone.registry.field.TextLine" />
    </field>
    <value>
      <element>tags</element>
      <element>friendly_type_name</element>
      <element>portal_type</element>
    </value>
  </record>

.. _plone.indexer: https://pypi.python.org/pypi/plone.indexer

Adding facets
-------------

Valid facets can be configured using the `ploneintranet.search.facet_fields` registry value. These will be returned on the :class:`ISearchResponse<ploneintranet.search.interfaces.ISearchResponse>` object (see below).


.. code:: xml

  <record name="ploneintranet.search.facet_fields">
    <field type="plone.registry.field.Tuple">
      <title>Facet field</title>
      <description>A field that will be used to facet query responses</description>
      <value_type type="plone.registry.field.TextLine" />
    </field>
    <value>
      <element>friendly_type_name</element>
      <element>tags</element>
    </value>
  </record>

Adding options to the site search interface
-------------------------------------------

The refinement options shown in the main search interface
are auto-generated from any fields registered as 
*both* a facet and a filter field (see above for adding facets/fields).

Adding search fields ('phrase fields')
--------------------------------------

To change the fields that are included in the text search query, use the `ploneintranet.search.phrase_fields` registry entry.

.. code:: xml

  <record name="ploneintranet.search.phrase_fields">
    <field type="plone.registry.field.Tuple">
      <title>Phrase fields</title>
      <description>Fields to which the main search phrase will be applied</description>
      <value_type type="plone.registry.field.TextLine" />
    </field>
    <value>
      <element>Title</element>
      <element>Description</element>
      <element>SearchableText</element>
    </value>
  </record>

Field boosting (Solr)
---------------------

To control the weighting/boosting of the phrase fields (see above), use the `ploneintranet.search.solr.phrase_field_boosts` registry entry.

.. code:: xml

  <record name="ploneintranet.search.solr.phrase_field_boosts">
    <field type="plone.registry.field.Dict">
      <title>Phrase query field and associated boost values</title>
      <description>Solr Boost values used to compute relevency for queries.</description>
      <key_type type="plone.registry.field.TextLine" />
      <value_type type="plone.registry.field.Int">
        <min>1</min>
      </value_type>
    </field>
    <value>
      <element key="Title">5</element>
      <element key="Description">3</element>
      <element key="SearchableText">2</element>
    </value>
  </record>



Using the Search Utility
========================

You can make custom calls to the search utility as follows:

.. code:: python

    from zope.component import getUtility
    from ploneintranet.search.interfaces import ISiteSearch

    sitesearch = getUtility(ISiteSearch)
    response = sitesearch.query(phrase='My search phrase')

    print 'Found {.total_results} result(s)'.format(response)
    result_tags = response.facets.get('tags')

The result of the 'query' call will implement the :class:`ISearchResponse <ploneintranet.search.interfaces.ISearchResponse>` interface:

.. autointerface:: ploneintranet.search.interfaces.ISearchResponse
   :members:

Iterating over the response will give an :class:`ISearchResult <ploneintranet.search.interfaces.ISearchResult>` for each matching result:

.. code:: python

    from zope.component import getUtility
    from ploneintranet.search.interfaces import ISiteSearch

    sitesearch = getUtility(ISiteSearch)
    response = sitesearch.query(phrase='My search phrase')

    for result in response:
        print 'Found a {.portal_type} named {.title}'.format(result)

.. autointerface:: ploneintranet.search.interfaces.ISearchResult
   :members:

The full query API is as follows:

.. autointerface:: ploneintranet.search.interfaces.ISiteSearch
   :members:



Debugging Search
================

package architecture
--------------------

The search package can appear a bit impenetrable because of the complex way
it has been engineered.

Two things to keep in mind:

- An original design goal was, to provide both ZCatalog and Solr support, and
  later ElasticSearch as well. However, ZCatalog is now deprecated because its
  feature set is too narrow. The code is still there though because of test
  dependencies.

- The implementation uses 'normal' ZCA Interfaces and Adapters, but also uses
  `Abstract Base Class`_, which is just a `different way of defining an interface`_.

.. _Abstract Base Class:  https://www.python.org/dev/peps/pep-3119/
.. _different way of defining an interface: http://griddlenoise.blogspot.nl/2007/05/abc-may-be-easy-as-123-but-it-cant-beat.html

The combination of these two can set you off on a goose chase if you're trying to
reconstruct the call flow in your mind.

The key entry point is `ploneintranet.search.solr.utilities.SiteSearch`.
This is the search utility that you're using instead of `portal_catalog`
so to speak.

`ploneintranet.search.solr.utilities.SiteSearch` implements the interface
`ploneintranet.search.interfaces.ISiteSearch` - but that's only the public interface
definition that only requires a `.query(...)` method. The rest of the interface
is defined elsewhere, hang on.

`ploneintranet.search.solr.utilities.SiteSearch` is a subclass of
`ploneintranet.search.base.SiteSearch` and it inherits its `.query(...)` implementation
and field definitions from that base implementation.

`ploneintranet.search.base.SiteSearch` in turn is registered whith the Abstract
Base Class `ploneintranet.search.base.SiteSearchProtocol`. In plone speak one
would say that `ploneintranet.search.base.SiteSearch` (and hence also the solr subclass)
*implements* the `ploneintranet.search.base.SiteSearchProtocol` *interface*.

In other words, due to the mixing of ZCA and ABC the interface contract definition
of the SiteSearch utility is defined in two places: a bit in the ZCA Interface
`ploneintranet.search.interfaces.ISiteSearch`, but most of the meat is defined
in the `ploneintranet.search.base.SiteSearchProtocol`. Don't get hung up on the
'Protocol' term, just think of it as a `SiteSearchInterface` in addition to the
"real" `ISiteSearch` interface.

The main difference is, that the ZCA interface is used to describe the public
interface contract, while the ABC registration is used to constrain the
private implementation method signature. That made sense at the time; however
these private implementation methods are now also being used elsewhere
(see 'power search' below), so there may be a case for future refactoring there.

The upshot of all that is, that both `ploneintranet.search.interfaces.ISiteSearch`
and `ploneintranet.search.base.SiteSearchProtocol` are interface contracts, not
actual code in the call flow.

call flow
---------

The call flow entry point is `ploneintranet.search.solr.utilities.SiteSearch.query()`
which is actually `ploneintranet.search.base.SiteSearch.query()` which then calls
a lot of `self._apply...` and other private methods, and finally `self.execute()`,
all of which do not exist in `base` but are implemented in
`ploneintranet.search.solr.utilities.SiteSearch`.
So you have to jump between `base` where the toplevel call flow is defined,
and `solr.utilities` where the actual implementation is.

The difference between `query()` and `execute()` is, that `query()` takes the
initial (user) query and then processes that with various extra filters, before
using `execute()` to actually query the Solr engine. The `execute()` method adds one
extra filter, to enforce security, and propagates the query parameters to the response,
so that the original query remains available to the application, especially for
subsequent filtering down by facet by the end user.

`ISiteSearch.query()` returns a `ploneintranet.search.interfaces.ISearchResponse`
which is implemented in `ploneintranet.search.solr.adapters.SearchResponse`, which
is subclassed from `ploneintranet.search.base.SearchResponse`. So you have to jump
between `base` and `solr.adapters` to understand that part.

`ISearchResponse` is basically an iterator over
`ploneintranet.search.interfaces.ISearchResult` items - analogous to a `ZBrain`
for ZCatalog query results. The implementation of that is in
in `ploneintranet.search.solr.adapters.SearchResult` which delegates almost
all of the heavy lifting to its superclass `ploneintranet.search.base.SearchResult`.

power search
------------

All of the above is when you use the search utility via the search page in Quaive.

An alternative usage scenario is, to use the power of Solr instead of ZCatalog when
constructing application code. An example of that can be found in
`ploneintranet.library.browser.views.utils`, which has a different
`query()` builder that operates directly on the `scorched query implementation`_.

.. _scorched query implementation: http://scorched.readthedocs.org/en/latest/query.html

debugging
---------

`ISiteSearch.query()` takes a `debug` argument. Set this to `True` to get an echo
of the solr query being fired off in the instance log.

In http://localhost:8983/solr/#/core1/query you can then start playing with the
query manually. You'll have to split the FilterQuery `fq` into its separate subqueries one by one.

Note that the `path_parents` syntax of the solr console is different from the scorched
notation. You'll have to replace `path_parents:\\/Plone\\/library`
with `path_parents:"/Plone/library"` i.e. remove escapes and add double quote wrapper.

Just like in ZCatalog, there's a difference between returned metadata and indexed values.
You can inspect the indices via e.g.
http://localhost:8983/solr/#/core1/schema-browser?field=path_parents
("Load Term Info").
