#!/bin/sh
#
# Shell script to manage .po files.
#
# Run this file in the folder main __init__.py of product
#
# E.g. if your product is yourproduct.name
# you run this file in yourproduct.name/yourproduct/name
#
#
# Copyright 2009 Twinapex Research http://www.twinapex.com
#

# Assume the product name is the current folder name
CURRENT_PATH=`pwd`
CATALOGNAME="ploneintranet"

# List of languages
LANGUAGES="en nl es fr it pt_BR"

# Create locales folder structure for languages
install -d locales
for lang in $LANGUAGES; do
    install -d locales/$lang/LC_MESSAGES
done

# Rebuild .pot
i18ndude rebuild-pot --exclude="generated prototype examples" --pot locales/$CATALOGNAME.pot --merge locales/manual.pot --create $CATALOGNAME ..

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do

    if test -d $lang/LC_MESSAGES; then

        PO=$lang/LC_MESSAGES/${CATALOGNAME}.po

        # Create po file if not exists
        touch $PO

        # Sync po file
        echo "Syncing $PO"
        i18ndude sync --pot locales/$CATALOGNAME.pot $PO

        # Compile .po to .mo
        MO=$lang/LC_MESSAGES/${CATALOGNAME}.mo
        echo "Compiling $MO"
        msgfmt -o $MO $lang/LC_MESSAGES/${CATALOGNAME}.po
    fi
done

# # Synchronise the templates and scripts with the .pot.
# i18ndude rebuild-pot --pot locales/plone.pot \
#     --create plone \
#     configure.zcml \
#     profiles/default/
#
# # Synchronise the Plone's pot file (Used for the workflows)
# for po in locales/*/LC_MESSAGES/plone.po; do
#     i18ndude sync --pot locales/plone.pot $po
# done
