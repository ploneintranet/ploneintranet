.. _configuration_using_portal_registry.rst:

===================================
Configuration using portal_registry
===================================

Plone intranet can be controlled by modifying the portal_registry.

The following registry records have beein configured through
the ploneintranet packages


ploneintranet.layout
--------------------

ploneintranet.layout.dashboard_activity_tiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: List of dashboard activity tiles

    **description**: This is the list of the tiles the user will see on the "Activity centric view" dashboard.

    **type**: plone.registry.field.Tuple composed of plone.registry.field.TextLine

    **default**: ./@@contacts_search.tile,
                 ./@@news.tile,
                 ./@@my_documents.tile

ploneintranet.layout.dashboard_task_tiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    tilte: List of dashboard activity tiles

    **description**: This is the list of the tiles the user will see on the "Activity centric view" dashboard.

    **type**: plone.registry.field.Tuple of plone.registry.field.TextLine

    **default**: ./@@contacts_search.tile,
                 ./@@news.tile,
                 ./@@my_documents.tile,
                 ./@@workspaces.tile?workspace_type=ploneintranet.workspace.workspacefolder,
                 ./@@workspaces.tile?workspace_type=ploneintranet.workspace.case,
                 ./@@events.tile,
                 ./@@tasks.tile,

ploneintranet.layout.dashboard_default
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    tilte: Name of the default dashboard

    **description**: This is the name of the dashboard type that should be shown by default. Pick the values from the dropdown on the dashboard.

    **type**: plone.registry.field.TextLine

    **default**: activity


ploneintranet.search
--------------------

ploneintranet.search.filter_fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Filter fields

    **description**: Fields that will be used to filter query responses in searches

    **type**: plone.registry.field.Tuple of plone.registry.field.TextLine

    **default**: tags,
                 friendly_type_name,
                 portal_type,
                 path,
                 is_division,
                 division


ploneintranet.search.facet_fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Facet field

    **description**: A field that will be used to facet query responses

    **type**: plone.registry.field.Tuple of plone.registry.field.TextLine

    **default**: tags,
                 friendly_type_name,
                 is_division,


ploneintranet.search.phrase_fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Phrase fields

    **description**: Fields to which the main search phrase will be applied

    **type**: plone.registry.field.Tuple of plone.registry.field.TextLine

    **default**: Title,
                 Description,
                 tags,
                 SearchableText


ploneintranet.search.solr.phrase_field_boosts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Phrase query field and associated boost values

    **description**: Solr Boost values used to compute relevency for queries.

    **type**: plone.registry.field.Dict {plone.registry.field.TextLine: plone.registry.field.Int}

    **default**: Title: 5
                 Description: 3
                 tags: 4
                 SearchableText: 1

    **note**: minimum accepted integer is 1


ploneintranet.search.ui.persistent_options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Persistent search options

    **description**: If this option is enabled, the selected search options will be stored for every user

    **type**: plone.registry.field.Bool

    **default**: False


ploneintranet.search.ui.additional_facets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Additional facets for filtering your results

    **description**: The search results page, by default,
                     facets the search results using the friendly_type_name field.
                     Here you can list additional fields you want to use for faceting.
                     Each field should be specified as field
                     (should match the values from ploneintranet.search.facet_fields)
                     and label
                     (a value that can be translate in the ploneintranet 18n domain)

    **type**: plone.registry.field.Dict {plone.registry.field.ASCII: plone.registry.field.TextLine}

    **default**: {'tags': 'Tags'}


ploneintranet.userprofile
-------------------------

ploneintranet.userprofile.hidden_fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Hidden fields

    **description**: User profile fields that are hidden from the profile editing page

    **type**: plone.registry.field.Tuple composed of plone.registry.field.TextLine

    **default**:

ploneintranet.userprofile.property_sheet_mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Property sheet mapping

    **description**: A mapping of a user property to a specific
                     property sheet which
                     should be used to obtain the data for this attribute.

    **type**: plone.registry.field.Dict {plone.registry.field.ASCII: plone.registry.field.TextLine}

    **default**:

ploneintranet.userprofile.primary_external_user_source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Primary External User Source

    **description**: The ID of the PAS plugin that will be treated as the primary source of external users.

    **type**: plone.registry.field.ASCIILine

    **default**:

ploneintranet.userprofile.read_only_fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Read only fields

    **description**: User profile fields that are read-only
                    (shown on profile editing page but not editable)

    **type**: plone.registry.field.Tuple composed of plone.registry.field.TextLine

    **default**: username

ploneintranet.userprofile.locations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Hidden fields

    **description**: User profile fields that are hidden from the profile editing page

    **type**: plone.registry.field.Tuple composed of plone.registry.field.TextLine

    **default**: London,
                 Amsterdam,
                 Berlin,
                 Paris,
                 New York


ploneintranet.workpace
----------------------

ploneintranet.workspace.case_manager.states
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Case Manager Workflow States

    **description**: Only these States are shown for filtering

    **type**: plone.registry.field.Tuple composed of plone.registry.field.TextLine

    **default**: new, pending, published, rejected

ploneintranet.workspace.externaleditor_always_activated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: External Editor always activated.

    **description**: When true, the isActivatedInMemberProperty()
                     and isActivatedInSiteProperty()
                     methods of the EnabledView always return True.
                     Otherwise the normal behaviour as implemented
                     in collective.externaleditor is used.

    **type**: plone.registry.field.Bool

    **default**: False

ploneintranet.workspace.my_workspace_sorting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: My workspace sorting.

    **description**: At the moment we are able to handle the values
                     "alphabet" and "newest".
                     Planned is to allow sorting on "active".

    **type**: plone.registry.field.TextLine

    **default**: alphabet

ploneintranet.workspace.workspace_types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Select workspace types

    **description**: Only this types are searched when looking for workspaces

    **type**: plone.registry.field.Tuple of plone.registry.field.TextLine

    **default**: ploneintranet.workspace.workspacefolder,
                 ploneintranet.workspace.case

    **note**: this will probably removed in favour of filtering
              by interface

ploneintranet.workspace.workspace_types_css_mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Maps workspace portal types to css classes

    **description**: If a portal_type is not here it will default to regular.
                     The values should be passed as "{type}|{css class}",
                     e.g. "ploneintranet.workspace.case|type-case"

    **type**: plone.registry.field.Tuple of plone.registry.field.TextLine

    **default**: ploneintranet.workspace.case|type-case


ploneintranet.workspace.sanitize_html
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    **title**: Sanitize HTML on saving.

    **description**: If set to True, RichText content (HTML) in workspaces is sanitized before it gets stored. That means all open tags are properly closed, and inline styles and unwanted tags such as ``<span>`` or ``<blockquote>`` get stripped. Multipe line breaks get reduced to a single line break.

    **type**: plone.registry.field.Bool

    **default**: True
