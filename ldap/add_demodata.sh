#!/bin/bash
env ldapadd -H ldap://127.0.0.1:8389 -f ploneintranet.ldif -D "cn=root,dc=ploneintranet,dc=com" -w secret
