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

Please submit a new pull request from the release branch into master.
Do not delete the release branch, it will be re-used for subsequent releases.

If you do this a lot, you probably want to add an alias into your .gitconfig::

    [alias]
	changelog = log --pretty='* %s [%cn]'

So then you can do `git changelog` instead of `git log --pretty='* %s [%cn]'`. YMMV.

Using a private egg release
===========================

To your non-public project buildout.cfg::

  [buildout]
  find-links +=
      http://user:password@pypi.quaive.net/packages/

  # we want to pull in development releases
  prefer-final = false


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
