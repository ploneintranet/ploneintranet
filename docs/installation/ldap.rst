==============
Optional: LDAP
==============

Ploneintranet can connect to an LDAP server to manage user information. LDAP support is deactivated by default, but it can be set up easily as ploneintranet comes with default configuration. This page will guide you through the process.

Preparations
------------

These instructions assume that you have openldap installed and that the slapd and ldapadd commands are available to you. On Ubuntu you can install them as follows::

    sudo apt-get install slapd
    sudo apt-get install ldap-utlis

ldapvi is not required, but it may come in handy. On Ubuntu you can install it by running::

    sudo apt-get install ldapvi

If you use the provided development Dockerfile, all that this is auto-installed for you.

The slapd.conf file requires the ldap schema files to be present inside the ldap/schema folder in your buildout directory. You can either create a link to the schema directory of your openldap installation::

    cd {buildout:directory}/ldap
    ln -s /etc/ldap/schema

or you can change the respective entries in the slapd.conf file to point to the paths in that schema directory.

.. warning::

   The provided `ldap/slapd.conf` is just a working example.
   You **must** change the suffix, rootdn and rootpw before deploying into production!

Setting up LDAP
---------------

After running buildout, supervisord can start an instance of slapd for you, however it does not do so automatically.
First start supervisord if you haven't already:

    bin/supervisord

To start slapd run the following command from your buildout directory::

    bin/supervisorctl start slapd

By default there will be no demo users in the directory. If you wish to import demo users, please change to the ldap folder in the buildout directory and run::

    ./add_demodata.sh

You *must* run the script from its parent directory or it will fail.

.. warning::

   Do **not** install the demo users into a production environment.

If you installed ldapvi you can verify that the users have been added by running::

    ldapvi -b "dc=ploneintranet,dc=com" -D "cn=root,dc=ploneintranet,dc=com" -h ldap://localhost:8389

You will be promted for the password, which is 'secret' by default. If you have not installed ldapvi, you can use ldapsearch instead.

Using a different ldap ldif
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To load a different ldif, e.g. supplied by a client, you'll have to:

- Change ``slapd.conf`` to reflect the right organisational name.

- Cleanup the provided ldif until it loads.

This `blog post <http://vaab.blog.kal.fr/2010/03/10/import-export-ldap-database/>`_ provides a good primer on cleaning up your ldif. 

Remove offending fields::

  egrep -v  "^(structuralObjectClass|entryUUID|creatorsName|modifiersName|createTimestamp|modifyTimestamp|entryCSN|entryDN|hasSubordinates|subschemaSubentry):" /var/tmp/foo-import/foo.ldif > /var/tmp/foo-import/foo-stripped.ldif

Clear database from previous failed attempts::

  ldapdelete -H ldap://127.0.0.1:8389 -r -D cn=root,dc=example,dc=org dc=example,dc=org -w secret

Load the new cleaned-up ldif::

  ldapadd -H ldap://127.0.0.1:8389 -f /var/tmp/foo-import/foo-stripped.ldif -D "cn=root,dc=example,dc=org" -w secret

You may have to iterate with loading/deleting the tree until you've found and stripped all offending fields - note that the egrep expression above contains more fields than the original from the blog post.


Connecting Plone to LDAP
------------------------

Now that LDAP itself is ready, you can go on to connect it to Ploneintranet. To create and configure the LDAP plugin, go to the ZMI and perform the 'Plone Intranet: LDAP' import step in portal_setup.

After that you still need to configure the port of the ldap server manually. To this end, navigate to acl_users/ldap-plugin/acl_users tab 'LDAP Servers' in the ZMI (Typical direct URL: http://localhost:8080/Plone/acl_users/ldap-plugin/acl_users/manage_servers ), delete the existing ldap server and create a new one with the host 'localhost' and the port '8389'.

The LDAP conntection is now set up and you can log into your Plone site as elda_pearson using the password 'secret' (or as any of the Ploneintranet test users, such as christian_stoney, etc.)


Using a different ldif
~~~~~~~~~~~~~~~~~~~~~~

You may have to change the suffix, rootdn and rootpw on the LDAPUserFolder configuration.

http://localhost:8080/Plone/acl_users/ldap-plugin/acl_users/manage_main

Also make sure your Users Base DN and Groups Base DN correspond to the ldif you've loaded.

Using LDAP in Ploneintranet
---------------------------

A new user logging in via LDAP, triggers the automatic creation of a matching Membrane profile
in ploneintranet.

The :doc:`../development/components/userprofiles` documentation provides further guidance
on leveraging LDAP in Ploneintranet:

- Periodically synchronizing userprofiles from LDAP
- Synchronizing user properties from LDAP
- Extending user properties

  
Uninstalling LDAP
-----------------

Should you wish to uninstall LDAP support, run the GenericSetup import step `Plone Intranet: Suite: LDAP Uninstall`.

Because `plone.app.ldap` does not provide an uninstall profile, you also have to manually remove the LDAP plugin from `acl_users` via the ZMI.
