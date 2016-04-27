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

The slapd.conf file requires the ldap schema files to be present inside the ldap/schema folder in your buildout directory. You can either create a link to the schema directory of your openldap installation or you can change the respective entries in the slapd.conf file to point to the paths in that schema directory.

Setting up LDAP
---------------

After running buildout, supervisord can start an instance of slapd for you, however it does not do so automatically. To start slapd run the following command from your buildout directory::

    bin/supervisorctl start slapd

By default there will be no demo users in the directory. If you wish to import demo users, please change to the ldap folder in the buildout directory and run::

    ./add_demodata.sh

You *must* run the script from its parent directory or it will fail.

If you installed ldapvi you can verify that the users have been added by running::

    ldapvi -b "dc=ploneintranet,dc=com" -D "cn=root,dc=ploneintranet,dc=com" -h ldap://localhost:8389

You will be promted for the password, which is 'secret' by default. If you have not installed ldapvi, you can use ldapsearch instead.

Connecting Plone to LDAP
------------------------

Now that LDAP itself is ready, you can go on to connect it to Ploneintranet. To create and configure the LDAP plugin, go to the ZMI and perform the 'Plone Intranet: LDAP' import step in portal_setup.

After that you still need to configure the port of the ldap server manually. To this end, navigate to acl_users/ldap-plugin in the ZMI, delete the existing ldap server and create a new one with the host 'localhost' and the port '8389'.

The LDAP conntection is now set up and you can log into your Plone site as elda_pearson using the password 'secret' (or as any of the Ploneintranet test users, such as christian_stoney, etc.)
