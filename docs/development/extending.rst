=============
Customization
=============

Ploneintranet does not subscribe to Plone's *Just a Bunch of Add-ons* paradigm.
Ploneintranet is a much more polished, integrated application than Plone can be,
because we sacrifice *generic framework-y-ness* to gain a highly integrated user experience.

Ploneintranet is Plone under the hood, obviously, so the required technical skills in developing and/or customizing Plone still apply. But the way we approach UX and UI engineering means **you cannot just customize Ploneintranet the way you would customize Plone**.


New Feature Development
=======================

The biggest difference between "normal" Plone practices and Ploneintranet, is that we have a great dislike for one-off customer-specific new feature development.
In our opinion, that leads to poor user experiences, creates technical debt and is just not cost-effective in the long run.

Instead, we analyse any specific customer requirement and generalize it into a generic feature that can be configured to satisfy *this* customer's need. Or we further generalize and extend an existing feature, until the new feature set can be configured to suit *all* our customer's needs.

As an integrator, this involves working with the product owner and UX designer.
Design is done in our non-Plone interactive prototype and results in a fully articulated clickable frontend that already provides all HTML, CSS and Javascript, but lacks a Plone backend. This prototype design is then implemented in Ploneintranet.

Typically, a new feature will result in not only a dedicated *app*, but also in various event hooks and UI actions througout the core system, interfacing with the new data structures. Bookmarking and change auditing are good examples of such new feature development that introduce both a very visible new app but also subtle enhancements (bookmark buttons, event listeners) throughout the stack.

New feature development requires access to the prototype, which means you'll have
to collaborate with an existing Quaive partner.


Tweaking Existing Features
==========================

Sometimes you don't want to create a complete new scope, but just want to change
an existing feature a little bit, or add a few data fields.

Because we aim to generalize and then to configure those generic features, you'll
find quite some configuration options in our backend. These are typically
registry driven, avoiding the need for code-level forking and customization.
For example the :doc:`./development/components/userprofiles` and
:doc:`./development/components/search` backends are excellently
tweakable this way.

Example: adding a new field
===========================

Below you'll find a worked example showing all steps required to make
a new field available, taken from an existing client project.

We'll add a multi-select field with a controlled vocabulary to a workspace.
The name of the field is `violations`.


Create a registry-powered vocabulary
------------------------------------

We could hardcode the vocabulary, but it's much more flexible to make it
configurable in GenericSetup. Create a new `registry.xml` record:

.. code:: xml

      <record name="my.package.violations">
        <field type="plone.registry.field.Dict">
            <title>Violations</title>
            <description xmlns:ns0="http://xml.zope.org/namespaces/i18n"
                         ns0:domain="my.package"
                         ns0:translate="help_violations">Violations</description>
            <key_type type="plone.registry.field.TextLine" />
            <value_type type="plone.registry.field.TextLine" />
        </field>
        <value>
          <element key="cutnrun">Cut and run</element>
          <element key="closure">Factory closure</element>
          <element key="unpaid">Unpaid compensation</element>
        </value>
      </record>

Now create the actual vocabulary in `vocabularies.py`, deriving the options
from the registry record we defined above:

.. code:: python
          
    from plone import api
    from zope.schema.vocabulary import SimpleTerm
    from zope.schema.vocabulary import SimpleVocabulary
    
    
    def violations(context):
        return registry2vocabulary('my.package.violations')
    
    
    def registry2vocabulary(record_id):
        records = api.portal.get_registry_record(record_id)
        terms = [SimpleTerm(value=key, token=key, title=records[key])
                 for key in records]
        terms.sort(cmp=lambda x, y: cmp(x.title, y.title))
        return SimpleVocabulary(terms)


Register the vocabulary in `configure.zcml`:

.. code:: xml

      <utility
          provides="zope.schema.interfaces.IVocabularyFactory"
          component=".vocabularies.violations"
          name="my.package.vocabularies.violations"
          />


Create a behavior with the new field
------------------------------------

Create a behaviors subdirectory in your package, touch `__init__.py` and create a custom module to contain your new behavior:

.. code:: python

    # -*- coding: utf-8 -*-
    from collective import dexteritytextindexer
    from plone.autoform.interfaces import IFormFieldProvider
    from plone.directives import form
    from ploneintranet.core import ploneintranetCoreMessageFactory as _
    from zope import schema
    from zope.interface import alsoProvides
    
    
    class IWorkspaceMetadata(form.Schema):
    
        dexteritytextindexer.searchable('violations')
        violations = schema.List(
            title=_(u"Violations"),
            value_type=schema.Choice(
                source=u"my.package.vocabularies.violations"),
            required=False,
        )
    
    alsoProvides(IWorkspaceMetadata, IFormFieldProvider)

Register the new behavior in `behaviors/configure.zcml`:

.. code:: xml
  
    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:plone="http://namespaces.plone.org/plone"
        i18n_domain="ploneintranet">
        
      <plone:behavior
          title="Urgent Appeal Metadata"
          description="Adds Urgent Appeal specific Metadata"
          provides=".urgentappeal.IWorkspaceMetadata"
          />
    
    </configure>

Enable the behaviors in your toplevel `configure.zcml`::

   <include package=".behaviors" />

Add the behavior to the registered `behaviors` in the FTI of your type::

     <element value="my.package.behaviors.urgentappeal.IWorkspaceMetadata" />
     <element value="collective.dexteritytextindexer.behavior.IDexterityTextIndexer" />


Set up indexing on the new field
--------------------------------

Create a new module `indexers.py`.

.. code:: python

    from .behaviors.urgentappeal import IWorkspaceMetadata
    from plone.indexer import indexer

     
    @indexer(IWorkspaceMetadata)
    def violations(obj):
        return hasattr(obj, 'violations') and obj.violations or None


Don't forget to add the collective.dexteritytextindexer dependency to your buildout or your custom egg `setup.py`.

Register the indexer in your toplevel `configure.zcml`::

   <adapter name="violations" factory=".indexers.violations" />

Add the index to the portal catalog, and also return indexed values in catalog 'brains'. In GenericSetup `catalog.xml`:

.. code:: xml

    <?xml version="1.0"?>
    <object name="portal_catalog" meta_type="Plone Catalog Tool">
      <index name="violations" meta_type="KeywordIndex">
      <indexed_attr value="violations"/>
     </index>
     <column value="violations"/>
    </object>


Index the new field in Solr. Also return the indexed value in the Solr 'brains'.
In your `buildout.cfg`, add::

    [core1]
    index +=
        name:violations             type:string indexed:true stored:true multivalued:true

Register the new field as a search facet, as a queryable index, and as a drilldown facet that should show up in the UI. In `registry.xml`:

.. code:: xml

      <record name="ploneintranet.search.facet_fields">
        <value purge="false">
          <element>violations</element>
        </value>
      </record>
    
      <record name="ploneintranet.search.filter_fields">
        <value purge="false">
          <element>violations</element>
        </value>
      </record>
    
      <record name="ploneintranet.search.ui.additional_facets">
        <value purge="false">
          <element key="violations">Violations</element>
        </value>
      </record>

   
Provide a custom browserlayer and override a view and template
--------------------------------------------------------------

Add a new browserlayer to `interfaces.py`.

.. code:: python
          
    # -*- coding: utf-8 -*-
    from ploneintranet.workspace.interfaces import IPloneintranetWorkspaceLayer

    class IMyWorkspaceLayer(IPloneintranetWorkspaceLayer):
        """
        Marker interface for requests indicating the my.package
        workspace is being used.
        """
    
Register the browserlayer in your GenericSetup `browserlayer.xml`.

.. code:: xml

    <?xml version="1.0"?>
    <layers>
      <layer
          name="my.package.workspace"
          interface="my.package.interfaces.IMyWorkspaceLayer"
          />
    </layers>


Re-implement the *General Settings* tile of the workspace sidebar.
In `browser/sidebar.py`:

.. code:: python

    # -* coding: utf-8 *-
    from ploneintranet.workspace.browser.tiles.sidebar import BaseTile
    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    from my.package.behaviors.urgentappeal import IWorkspaceMetadata
    from my.package import vocabularies
    
    
    class SidebarSettingsGeneral(BaseTile):
        """ A view to serve as the advanced config in the sidebar
        """
    
        index = ViewPageTemplateFile('templates/sidebar-settings-general.pt')
    
        def __call__(self):
            """ write attributes, if any, set state, render
            """
            self._basic_save()
            return self.render()
    
        def has_my_metadata(self):
            return IWorkspaceMetadata.providedBy(self.workspace())
    
        def violations(self):
            selected = IWorkspaceMetadata(self.workspace()).violations
            for term in vocabularies.violations(self.context):
                term.selected = term.value in selected and 'selected' or ''
                yield term

Copy the upstream `ploneintranet/workspace/browser/tiles/templates/sidebar-settings-general.pt` into `./browser/templates/`.

Then, add our custom field multi-select:

.. code:: xml

      <tal:enabled condition="view/has_my_metadata">
        <label class="pat-select">
           <span tal:omit-tag="" i18n:translate="workspace_violations">
           Violations</span>
           <select name="violations" multiple
                   tal:attributes="disabled not: view/can_manage_workspace;"
              <option tal:repeat="item view/violations"
                      value="${item/value}"
                      tal:attributes="selected item/selected">
                      ${item/title}</option>
          </select>
       </label>
     </tal:urgentappeal>
                

Register the tile override in `browser/overrides.zcml`.

.. code:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser"
        xmlns:i18n="http://namespaces.zope.org/i18n"
        xmlns:plone="http://namespaces.plone.org/plone"
        i18n_domain="ploneintranet.workspace">
    
      <plone:tile
          name="sidebar.settings.general"
          title="General settings"
          description=""
          add_permission="cmf.ManagePortal"
          class=".sidebar.SidebarSettingsGeneral"
          permission="zope2.View"
          for="*"
          layer="my.package.interfaces.IMyWorkspaceLayer"
          />
      
      
    </configure>

Register the browser overrides in your toplevel `overrides.zcml`.

.. code:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:five="http://namespaces.zope.org/five"
        xmlns:i18n="http://namespaces.zope.org/i18n"
        xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
        i18n_domain="ccc.insite">

      <include package=".browser" file="overrides.zcml"/>
  
    </configure>

This will get picked up automatically by `z3c.autoinclude` on Plone restart.

Done
----

Obviously, you'll have to re-buildout, start Ploneintranet, create a site and load your `my.package` GenericSetup profile. When all is well, you'll have a new field on the *Generic Settings* tab of a workspace. Saving some values there and searching for the changed workspaces should show the custom facet in the search results sidebar.


