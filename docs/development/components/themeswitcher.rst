==============
Theme Switcher
==============

``ploneintranet.themeswitcher`` makes it possible to access a Plone Intranet
site styled in the default Plone5 Barceloneta theme, instead of in the
Plone Intranet theme.

The reason for doing this is, that not all parts of the Plone user interface
are supported in Plone Intranet. Our goal is to first support all the
user interface used by a "typical" user. That excludes pages like the
control panels which are only used by site administrators.

Up to Plone 4 theme switching was a normal practice, and supported by for example collective.themeswitcher.

In Plone 5, the theming implementation has changed in ways that make theme switching much more difficult, because it depends on registry settings stored in the ZODB and of the way themes are cached for performance.

.. note::

   ``ploneintranet.themeswitcher`` depends on changes in ``Products.CMFPlone`` and
   ``plone.app.theming``. These are now run as forks until the required changes to
   support theme switching have been merged and released.


How theme switching works
=========================

Theme switching is implemented based on host name. Out of the box,
if you run Plone Intranet on localhost:8080/Plone you will be able to
access that same site styled in Barceloneta on cms.localhost:8080/Plone.
Of course that requires a ``/etc/hosts`` alias.

For production, you can configure theme switching to be triggered by a
different host name, by configuring it in the registry via GenericSetup,
in the ``hostname_switchlist`` record of ``IThemeSwitcherSettings``.

The default theme switching configuration in Plone Intranet is applied
in ``ploneintranet.suite:default`` as follows::

  <registry>
    <records
        interface="ploneintranet.themeswitcher.interfaces.IThemeSwitcherSettings">
      <value key="enabled">True</value>
      <value key="fallback_theme">barceloneta</value>
      <value key="fallback_rules">/++theme++barceloneta/rules.xml</value>
      <value key="fallback_absoluteprefix">/++theme++barceloneta</value>
      <value key="hostname_default">localhost</value>
      <value key="hostname_switchlist">
        <element>cms.localhost</element>
      </value>
      <value key="browserlayer_filterlist">
        <element>ploneintranet.theme.interfaces.IThemeSpecific</element>
      </value>
      <value key="fallback_enabled_bundles"></value>
      <value key="fallback_disabled_bundles">
        <element>ploneintranet</element>
      </value>
    </records>
  </registry>

All of these records are described in ``ploneintranet/themeswitcher/interfaces.py``.


Theming Policy
--------------

To support theme switching, in ``plone.app.theming`` we've introduced a ``ThemingPolicy`` API that is called as an adapter on ``request``. In ``ploneintranet.themeswitcher`` a custom policy adapter is registered::

    <adapter
        factory=".policy.SwitchableThemingPolicy"
        for="ploneintranet.themeswitcher.interfaces.IThemeSwitcher"
        />

Because this adapter is bound to a custom browserlayer, it takes precedence over 
the default adapter in ``plone.app.theming`` which is bound to ``zope.publisher.interfaces.IRequest`` - our browserlayer is a subclass of that hence more specific.

Note that this is a normal ZCA registration in ``configure.zcml``, which is sufficient to override the default policy without needing ``overrides.zcml``.

Our custom policy adapter subclasses the default policy.

Settings
--------

Normally, theme settings are stored in the ZODB in the form of registry records.
Because the registry is not layered, that means the original Barceloneta records
got overwritten when we installed ``ploneintranet.theme``. 

For normal rendering that is not a problem, we just access the registry and get
the values for ``ploneintranet.theme`` which is the default theme.

If we want to fallback to Barceloneta though, 
``ploneintranet.themeswitcher`` uses a ``SwitchableRecordsProxy`` that 
takes most of the fallback settings from the actual registry records 
for the default theme (ploneintranet), but returns
some "fake" records for the fallback theme (barceloneta) where needed.

The record overrides for the fallback theme can be configured in GenericSetup.
The fallback settings provided as defaults here were obtained by comparing,
in pdb, the theme settings for a default Barcelonta site, with the values returned
for a Plone Intranet themed site. YMMV.

Hostname Switching
^^^^^^^^^^^^^^^^^^

A special helper method decides whether to return the normal settings or the
fallback settings, based on the hostname contained in the request.

You can configure hostnames that activate the fallback theme via GenericSetup.

Development mode switching
^^^^^^^^^^^^^^^^^^^^^^^^^^

Additionally, when running in development mode you can trigger a theme fallback
by setting ``?themeswitcher.fallback=1`` on the URL. That does not propagate
across links though so you normally are better off as a developer to set up
a /etc/hosts alias for ``cms.localhost`` and accessing your site on cms.localhost
if you want to work with the fallback theme.

Cookie switching
^^^^^^^^^^^^^^^^

In theory we could also switch based on a cookie value in the request.
The downside of that is, that you start serving differently themed pages
on the same URL. That's bound to wreak havoc when combined with caching.


Switching Site Action
---------------------

A special helper view ``@@switch_theme`` is provided as a site action to switch between
the main theme and the fallback theme.

By using a different hostname for the fallback themed site we avoid
such caching conflicts. For the main site it uses the ``hostname_default`` registry
setting; for the fallback site it uses the first hostname listed in ``hostname_switchlist``.

Calling ``@@switch_theme`` replaces the hostname in the current URL and redirects
to the other site, either from main to fallback or the other way around, depending where
you are.


Request Mangler
---------------

In addition to the settings switching described above, we also need to manipulate
the request object to get Barceloneta to work properly.

``ploneintranet.themeswitcher`` registers an event subscriber that enables us to mangle the request in a way that is needed for theme switching to work::

    <subscriber
        for="plone.app.layout.navigation.interfaces.INavigationRoot
             zope.app.publication.interfaces.IBeforeTraverseEvent"
        handler=".policy.filter_request"
        />

This handler delegates to a method on the theming policy, that:

- Removes any browser layers that conflict with the fallback theme.
  Typically that is your own theme layer which extends CMFDefault.
  You should not extend CMFDefault for non-theme browser layers.

- Disables our custom resource bundle(s) by setting a special variable
  on the request that gets picked up by CMFPlone.

Both the browser layers to be removed and the bundle disabling can be
configured via GenericSetup.

Re-using ploneintranet.themeswitcher
====================================

``ploneintranet.themeswitcher`` has been set up as a generically re-usable
package. It has no dependencies on the rest of the ploneintranet stack.
All ploneintranet-specific themeswitcher settings are made outside
of the themeswitcher package in ``ploneintranet.suite``.

Even though it's part of the single ``ploneintranet`` egg, in the python sense ``ploneintranet.themeswitcher`` is a separate package. It has it's own GenericSetup profile and it's own test suite.

To re-use it, you can add the ``ploneintranet`` egg to your buildout,
and then in your own GenericSetup:

- Declare an installer dependency on ``ploneintranet.themeswitcher:default``
- Configure your own registry.xml settings.

In other words, you need to pull in the whole of ploneintranet but install only
ploneintranet.themeswitcher. 

Generalizing ploneintranet.themeswitcher
----------------------------------------

This package should probably be factored out into ``collective.themeswitcher``.
Like all of ploneintranet, the code is GPL and anybody is welcome to make 
that happen. The main things to work on are:

- Reconciling the policy adapter approach, which we now have contributed
  to ``plone.app.theming``, with the slightly different ``switcher``
  multi-adapters used in ``collective.themeswitcher``.

- Add/port missing features, like the mobile agent switching.

- Make a decision on whether or not to drop support for CMF skin layer
  switching support.

None of the above is needed for the Plone Intranet project but we're happy
to collaborate with anybody who needs those and wants to make an effort
to generalize the ``ploneintranet.themeswitcher`` code into a collective
package.
