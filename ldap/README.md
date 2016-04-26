LDAP configuration for ploneintranet
====================================

These instructions assume that you have openldap installed and that the slapd and ldapadd commands are available to you.

After running buildout, supervisord can start an instance of slapd for you, however it does not do so automatically. Run 'bin/supervisorctl start slapd' from your buildout directory to start slapd.

By default there will be no demo users in the directory. If you wish to import demo users, please run the add_demodata.sh script in the ldap directory. You must run the script from its parent directory. You can verify that the users have been added by runnung 'ldapvi -b "dc=ploneintranet,dc=com" -D "cn=root,dc=ploneintranet,dc=com" -h ldap://localhost:8389'. You will be promted for a password, which is 'secret' by default (it can be changed in the slapd.conf file).

To create and configure the ldap plugin, perform the 'Plone Intranet: LDAP' import step in portal_setup. After that you still need to configure the port of the ldap server manually. To this end, navigate to acl_users/ldap-plugin in the ZMI, delete the existing ldap server and create a new one with the host 'localhost' and the port '8389'.

You can now log into your Plone site as elda_pearson using the password 'secret' (or as any of the Ploneintranet test users, such as christian_stoney, etc.)
