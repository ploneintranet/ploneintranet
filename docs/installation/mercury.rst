==================================
Mercury Technology Preview Install
==================================

.. admonition:: Description

    This document describes how to install the Plone Intranet Mercury Technology Preview.

The Mercury Technology Preview is a milestone release aimed at `Plone Intranet Consortium`_ partners
and interested developers in the Plone community.

This follows Jason Friedman's mantra: release half a product, not a half-assed product.
Essential features are still missing, but the features we do ship are pretty exciting:

- A rich microblogging activity stream, with attachments, attachment previews, mentions, tagging, replies and likes.
- Secure collaboration workspaces with a rich local activity stream, strong document management with faceted navigation and previews, and intuitive security configuration management.

.. note::

   Plone Intranet Mercury Technology Preview is *not* a finished product. It's a preview.
   The preview lacks essential features, like managing users, managing content, and search.

If you want a complete product, please wait for our next milestone release, codenamed ``Venus``.

If you're not a Plone developer and interested in our technology, please contact one of the
`Plone Intranet Consortium`_ partners to arrange for a demo. They will be able to show you our current
design prototype, and provide you with specific insights into our roadmap and release planning.

If you're a Plone dev and want to try the Mercury preview now, follow the steps below.


Prepare the Operating System Environment
----------------------------------------

Make sure you have the OS-level packages you need to build Plone, this can be
achieved using `install.plone.dependencies`_.

In addition, for the Plone Intranet file preview functionality, you need docsplit.
On Ubuntu::

    sudo apt-get install ruby
    gem install docsplit

You will need some other tools installed for docsplit.  See the
`docsplit installation instructions`_.  Note that Libre Office is
mentioned as optional there, but in Plone Intranet we require it.


Create and run buildout
-----------------------

We assume you're familiar with basic Plone buildout.
If you're not, this preview is not for you.

Create a minimal buildout.cfg somewhere::

  [buildout]
  extends = https://raw.githubusercontent.com/ploneintranet/ploneintranet/mercury/mercury.cfg

Now, run the buildout::

  virtualenv .
  ./bin/pip install zc.buildout
  ./bin/buildout

If that works, you can start Plone::

  ./bin/instance fg


Create a new Plone instance
---------------------------

- Goto the Zope Management Interface at http://localhost:8080.
- Create a new Plone instance.
- In the Zope Management Interface, go to `portal_setup > import`_.
- Select Profile `Plone Intranet: Suite : Create Testing Content`.
- Scroll down to the bottom of the page and hit the button "Import all steps" - make sure "Include dependencies" is checked.

This activates Plone Intranet and sets up some demo users and workspaces so you can see what's possible.

.. warning::

   Do NOT install this on a production site. The test content install is irreversible.
   It will create fake users with insecure passwords.

You can now go to the site at http://localhost:8080/Plone.
However, don't do this logged in as admin in the ZMI.
Logout, or open a new browser window (use Chrome).
It will prompt you to log in. The test content setup created some users you can use.
You can log in as ``allan_neece`` (password: ``secret``) to play around as a default user.
User ``christian_stoney`` (password: ``secret``) is a workspace admin with more permissions.
User ``alice_lindstrom`` (password: ``secret``) is not a member of any workspaces, so you can see the difference there.
Those passwords are not actually secret, they're just the word "secret" without quotes!

.. note::

   If you end up with an empty site, you probably installed Plone Intranet Suite via the Plone Add-ons configuration screen.
   In a default empty site there's no way to manage users, so you won't be able to experience Plone Intranet as intended.
   Instead you should exactly follow the ZMI install procedure detailed above to install test users and test content.


Feedback
--------

As said, this is just a preview release and we're very aware that it's far from feature complete.
Please don't file tickets about missing features.

Any system of this level of complexity will have some hidden bugs.
If you find one, please let us know at http://github.com/ploneintranet/ploneintranet/issues.
A traceback and an exact description of what you were doing would be very helpful.

.. _Plone Intranet Consortium: http://ploneintranet.com
.. _`docsplit installation instructions`: https://documentcloud.github.io/docsplit/
.. _`install.plone.dependencies`: https://github.com/collective/install.plone.dependencies
.. _portal_setup > import: http://localhost:8080/Plone/portal_setup/manage_importSteps

