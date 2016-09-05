from ploneintranet.fastest import Strategy, Policy

workspaces = Strategy('workspaces')
workspaces.triggers = [
    'case.robot',
    'content_views.robot',
    'test_bulk_actions.robot',
    'workspace.robot',
    'src/ploneintranet/workspace',
    'src/ploneintranet/attachments',
    'src/ploneintranet/api/previews.py',
]
workspaces.packages = [
    'ploneintranet.workspace',
    'ploneintranet.todo',
    'ploneintranet.attachments',
    'ploneintranet.docconv',
]
workspaces.tests = [
    'case.robot',
    'content_views.robot',
    'test_bulk_actions.robot',
    'workspace.robot',
]

stream = Strategy('stream')
stream.triggers = [
    'test_microblog_security',
    'post_file.robot',
    'posting.robot',
    'src/ploneintranet/microblog',
    'src/ploneintranet/activitystream',
    'src/ploneintranet/api/microblog',
]
stream.packages = [
    'src/ploneintranet/microblog',
    'src/ploneintranet/activitystream',
    'src/ploneintranet/api',
]
stream.tests = [
    'test_microblog_security',
    'post_file.robot',
    'posting.robot',
]

search = Strategy('search')
search.triggers = [
    'search.robot',
    'src/ploneintranet/search'
]
search.packages = [
    'src/ploneintranet/search',
    'src/ploneintranet/search/solr'
]
search.tests = [
    'search.robot',
]

force_all = Strategy('force all')
force_all.wildcard = True
force_all.triggers = [
    'setup.py',
    'buildout.d',
    'src/ploneintranet/suite',
    'src/ploneintranet/theme',
    'src/ploneintranet/layout',
]

POLICY = Policy(workspaces, stream, search, force_all)
