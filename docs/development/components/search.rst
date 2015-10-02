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
