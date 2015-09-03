=============
User Profiles
=============

Plone Intranet is designed to provide an out-of-the-box user profile which provides the following:

 * Authentication (using dexterity.membrane_)

 * Customisable profile fields (using dexterity behaviours which can be disabled or overriden)

 * Support for external data sources (e.g. AD/LDAP)

The following key design decisions were made to fit the use cases of Plone Intranet:

 * **Users as content**

   Rather than using default plone members, we use dexterity.membrane_ to create real dexterity content that can be managed in the same way as all other content, whilst still providing authentication.

 * **Username as Userid**

   The default membrane implementation uses UUIDs as the unique id that Plone uses to grant roles and permissions (userid). We use the username instead, to ensure compatibility with external authentication sources such as AD/LDAP which have no knowledge of Plone's UUIDs.

.. _dexterity.membrane: https://pypi.python.org/pypi/dexterity.membrane/

Bulk Upload
===========

There is a bulk upload from CSV option. Column names are mapped to field names, and the data is validated before users are created:

To use the bulk upload, visit the `@@import-users` browser view on the profiles folder in your site:

.. code::

   /plonesite/profiles/@@import-users

Customising User Profiles
=========================

User profiles are expected to be highly customised for each Plone Intranet deployment. As such, the profile views are built dynamically from dexterity behaviours, and support extra options such as hidden or read-only fields.

Vocabularies
------------

The following vocabularies can be customised
using their corresponding plone.app.registry_ entries
(e.g. using GenericSetup).

 * **Primary Location** : ploneintranet.userprofile.locations

.. _plone.app.registry: https://pypi.python.org/pypi/plone.app.registry

Adding/Removing fields
----------------------

The User Profile comes with a base set of fields that are required by the Plone Intranet templates. These fields are as follows:

.. autointerface:: ploneintranet.userprofile.content.userprofile.IUserProfile
   :members:

There is also an additional set of (optional) fields. The optional fields are provided by the behaviour :class:`IUserProfileAdditional <ploneintranet.userprofile.content.userprofile.IUserProfileAdditional>`

You can remove the optional fields by disabling the `IUserProfileAdditional` behaviour in your GenericSetup profile. For more information on adding/removing behaviours using GenericSetup, see docs.plone.org_.

To add new fields, simply create a new behaviour and assign it to the ploneintranet.userprofile.userprofile type. For more information on adding custom field behaviours, see the Behaviours_ manual.

Hiding fields
-------------

To hide fields from the UI, add the relevant field name to the `ploneintranet.userprofile.hidden_fields` registry entry using GenericSetup:

.. code-block:: xml

  <record name="ploneintranet.userprofile.hidden_fields">
    <field type="plone.registry.field.Tuple">
      <title>Hidden fields</title>
      <description>
        User profile fields that are hidden from the profile editing page
      </description>
      <value_type type="plone.registry.field.TextLine" />
    </field>
    <value>
      <element>first_name</element>
      <element>MyCustomBehaviour.my-hidden-fieldname</element>
    </value>
  </record>

Read-only fields
----------------

To mark a field as 'read only' in the UI (but leave the field editable via code), add the relevant field name to the `ploneintranet.userprofile.read_only_fields` registry entry using GenericSetup.

This is useful for field data that comes from a separate source (e.g. AD/LDAP)

.. code-block:: xml

  <record name="ploneintranet.userprofile.read_only_fields">
    <field type="plone.registry.field.Tuple">
      <title>Read only fields</title>
      <description>
        User profile fields that are read-only
        (shown on profile editing page but not editable)
      </description>
      <value_type type="plone.registry.field.TextLine" />
    </field>
    <value>
      <element>username</element>
      <element>MyCustomBehaviour.my-read-only-fieldname</element>

    </value>
  </record>


External data sources (e.g. AD/LDAP)
======================================

The Plone Intranet UI always uses the membrane profile data as the source of
user data, to ensure a consistent experience when assigning roles, searching
or browsing users.

However, it is possible to configure specific membrane properties to be
regularly synchronised with an external data source (such as AD/LDAP) using
Plone's PAS properties infrastructure.

Property sheet mapping
----------------------

The registry entry `ploneintranet.userprofile.property_sheet_mapping` allows each user profile field to be mapped to a specific PAS plugin (using the id of the PAS plugin inside acl_users):

.. code-block:: xml

  <record name="ploneintranet.userprofile.property_sheet_mapping">
    <field type="plone.registry.field.Dict">
      <title>Property sheet mapping</title>
      <description>
        A mapping of a user property to a specific property sheet which
	should be used to obtain the data for this attribute.
      </description>
      <key_type type="plone.registry.field.ASCII" />
      <value_type type="plone.registry.field.TextLine" />
    </field>
    <value>
      <element key="username">ldap_plugin</element>
      <element key="email">another_pas_plugin</element>
    </value>
  </record>

External property synchronisation
---------------------------------

The `sync-users` browser view is available on the `profiles` directory,
and will use the above mapping to copy the relevant properties from the
relevant PAS plugin property sheet, and store it on the membrane profile.

It supports *any* PAS plugin that provides PAS properties for a user,
and will update *all* existing membrane profiles every sync,
so could be expensive depending on the number of users in your site.

The view requires Manager privileges.

.. code::

   /plonesite/profiles/@@sync-users

You can also sync an individual user profile using the `sync` view.
This view also requires Manager privileges.
		 
.. code::

   /plonesite/profiles/joe-bloggs/@@sync

Specific AD/LDAP synchronisation
--------------------------------

If you have plone.app.ldap_ installed, a separate AD/LDAP view is provided
that will query the AD server for any users that have changed since the
last sync (using the `whenChanged` AD attribute).

This significantly improves the performance of the sync:
   
.. code::

   /plonesite/profiles/@@sync-users-ldap
   
.. _docs.plone.org: http://docs.plone.org/external/plone.app.dexterity/docs/advanced/behaviours.html

.. _Behaviours: http://docs.plone.org/external/plone.app.dexterity/docs/behaviors/index.html

.. _plone.app.ldap: https://pypi.python.org/pypi/plone.app.ldap

User Profile API
================

.. automodule:: ploneintranet.api.userprofile
    :members:
    :undoc-members:
    :show-inheritance:
