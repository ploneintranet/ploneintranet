=============
User Profiles
=============

Plone Intranet is designed to provide an out-of-the-box user profile which provides the following:

 * Authentication (using `dexterity.membrane`)

 * Customisable profile fields (using dexterity behaviours which can be disabled or overriden)

The following key design decisions were made to fit the use cases of Plone Intranet:

Users as content
----------------

Rather than using default plone members, we use `dexterity.membrane` to create real dexterity content that can be managed in the same way as all other content, whilst still providing authentication.

Username as Userid
------------------

The default membrane implementation uses UUIDs as the unique id that Plone uses to grant roles and permissions (userid). We use the username instead, to ensure compatibility with external authentication sources such as LDAP which have no knowledge of Plone's UUIDs.

Bulk Upload
-----------

There is a bulk upload from CSV option. Column names are mapped to field names, and the data is validated before users are created:

To use the bulk upload, visit the `@@import-users` browser view on the profiles folder in your site:

.. code::

   /plonesite/profiles/@@import-users

User Profile API
----------------

.. automodule:: ploneintranet.api.userprofile
    :members:
    :undoc-members:
    :show-inheritance:
