Error Reference
=================

.. admonition:: Description

        Common Python exception traceback patterns you may encounter when
        working with Plone Intranet and possible solutions for them.

        Please see `this tutorial <http://docs.plone.org/manage/troubleshooting/basic>` for extracting
        Python tracebacks from your Plone logs.

Add-on installer error: This object was originally created by a product that is no longer installed
---------------------------------------------------------------------------------------------------

**Traceback**::

    2009-10-18 13:11:20 ERROR Zope.SiteErrorLog 1255860680.760.514176531634 http://localhost:8080/twinapex/portal_quickinstaller/installProducts
    Traceback (innermost last):
      Module ZPublisher.Publish, line 125, in publish
      Module Zope2.App.startup, line 238, in commit
      Module transaction._manager, line 93, in commit
      Module transaction._transaction, line 325, in commit
      Module transaction._transaction, line 424, in _commitResources
      Module ZODB.Connection, line 541, in commit
      Module ZODB.Connection, line 586, in _commit
      Module ZODB.Connection, line 620, in _store_objects
      Module ZODB.serialize, line 407, in serialize
      Module OFS.Uninstalled, line 40, in __getstate__
    SystemError: This object was originally created by a product that
                is no longer installed.  It cannot be updated.
                (<Salt at broken>)

**Reason**: Data.fs contains objects for which the code is not present.
You have probably moved Data.fs or edited buildout.cfg.

**Solution**: Check that eggs and zcml contain all necessary products in buildout.cfg.

.. seealso::
    * http://article.gmane.org/gmane.comp.web.zope.plone.setup/3232
