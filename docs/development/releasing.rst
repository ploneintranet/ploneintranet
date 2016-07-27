==============
Releasing eggs
==============

Introduction
============

We maintain two egg distributions:

1. Quaive private enterprise edition on pypi.quaive.net

2. Ploneintranet community edition on pypi.python.org

Each of those is managed on a separate release branch.
Quaive is currently on branch 1.1.x, Community is on 1.0.x.

These branches are needed so changes made during the release process
are QA controlled via the normal pull request process.

Since version 1.2.0a3,
we depend on the pacakge `quaive.resources.ploneintranet`.

Creating a release
==================

This shows how to cut a private 1.1.x release from master::

    user@host:~$ git checkout master
    user@host:~$ git pull
    user@host:~$ git checkout release-1.1.x
    user@host:~$ git pull
    user@host:~$ git merge master
    user@host:~$ git tag --list
    user@host:~$ # select right tag for command below
    user@host:~$ git log --pretty='* %s [%cn]' 1.1.0a2.. > /tmp/changes
    user@host:~$ sed -i '/- Nothing changed yet./ r /tmp/changes' CHANGES.rst
    user@host:~$ sed -i '/- Nothing changed yet./d' CHANGES.rst
    user@host:~$ git commit -am 'Update changelog'
    user@host:~$ bin/check-manifest
    user@host:~$ # fix MANIFEST.in until check-manifest passes
    user@host:~$ git commit -am 'Update manifest'
    user@host:~$ bin/fullrelease
    INFO: Starting prerelease.
    Run pyroma on the package before tagging? (Y/n)? Y
    Do you want to run check-manifest? (Y/n)? Y
    Enter version [1.1.0a3]:
    OK to commit this (Y/n)? Y
    INFO: Starting release.
    Tag needed to proceed, you can use the following command:
    git tag 1.1.0a3 -m "Tagging 1.1.0a3"
    Run this command (Y/n)? Y
    Check out the tag (for tweaks or pypi/distutils server upload) (Y/n)? Y
    Register and upload to pypi (Y/n)? n
    Register and upload to quaive (Y/n)? Y
    Register and upload to cosent (Y/n)? n
    INFO: Starting postrelease.
    Enter new development version ('.dev0' will be appended) [1.1.0a4]:
    OK to commit this (Y/n)? Y
    OK to push commits to the server? (Y/n)? Y

Please make sure to *not* push a private release to pypi.python.org!

The new release is now available on pypi.quaive.net and on Github.

If you do this a lot, you probably want to add an alias into your .gitconfig::

    [alias]
	changelog = log --pretty='* %s [%cn]'

So then you can do `git changelog` instead of `git log --pretty='* %s [%cn]'`. YMMV.

Merge the release changes
-------------------------

Please submit a new pull request from the release branch into master.
Do not delete the release branch, it will be re-used for subsequent releases.

See :doc:`gitflow` for a full description of the Git workflow.

Update the gaia deployment
--------------------------

We want to quality-check the new egg release by running a CI test on it.

If you don't have a `gaia` build already, initialize it, see below.

The Gaia buildout assumes that it's `buildout.d` directory is identical to the
ploneintranet `buildout.d` directory.
If your release involved a change in `ploneintranet/buildout.d` e.g. a Plone upgrade,
a new version pinning, or a new solr field, copy all the buildout.d configs to gaia::

  cp buildout.d/* ../gaia/buildout.d/  # or wherever your gaia build lives

Now go to `gaia`, update the `ploneintranet` pin::

  cd ../gaia  # or wherever your gaia build lives
  sed -i 's/ploneintranet = .*/ploneintranet = 1.1.0a5/' buildout.cfg
  git commit -am 'Release 1.1.0a5'

Obviously you're supposed to change the release number to match the actual release
you created above!

Finally, trigger a CI build by pushing the change::

  git push gitlab master
  git push origin master


Initializing a gaia deploy build
================================

If you don't have a `gaia` build already, check it out::

  git clone git@github.com:quaive/gaia.git

Add a remote for Gitlab pushes::

  git remote add gitlab git@gitlab.com:quaive/gaia.git


Using a private egg release
===========================

To your non-public project buildout.cfg::

  [buildout]
  find-links +=
      http://user:password@pypi.quaive.net/packages/

  # we want to pull in development releases
  prefer-final = false

You can use the `gaia` egg based deployment as a template.

Update `quaive.resources.ploneintranet`
=======================================

This process requires to clone separetely `quaive.resources.ploneintranet`
and releasing it to `pypi.quaive.net`::

  git clone git@github.com:quaive/quaive.resources.ploneintranet.git
  cd quaive.resources.ploneintranet
  make all
  fullrelease

Take note of the released egg version,
and update the file `buildout.d/versions.cfg`
in order to match it, e.g.::

  [versions]
  # Quaive packages
  quaive.resources.ploneintranet = 1.2.0a1

Make a pull request to `quaive/ploneintranet` with this changes.

Managing users on pypi.quaive.net
=================================

You can only add users if you have shell access::

    user@host$ ssh pypi@pypi.quaive.net
    pypi@cs02:~$ cd pypiserver/
    pypi@cs02:~/pypiserver$ htpasswd var/quaive/htpasswd.txt johndoe
    New password:
    Re-type new password:
    Adding password for user johndoe

Ask Guido to add your users if you do not have ssh access.
