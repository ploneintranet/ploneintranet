import collections

from scorched import search


class SpellcheckOptions(search.Options):
    """Alternate SpellcheckOptions implementation.

    This implements sub-options for the Solr spellchecker.
    The scorched implementation just allows turning it on.

    This may be pushed back upstream if deemed successfull.
    """
    option_name = 'spellcheck'
    opts = {
        'accuracy': float,
        'collate': bool,
        'maxCollations': int,
        'onlyMorePopular': bool,
        'extendedResults': bool,
        'q': str,
        'reload': bool,
        'build': bool,
    }

    def __init__(self, original=None):
        super(SpellcheckOptions, self).__init__()
        fields = collections.defaultdict(dict)
        self.fields = getattr(original, 'fields', fields)

    def field_names_in_opts(self, opts, fields):
        if fields:
            opts[self.option_name] = True


class Search(search.SolrSearch):

    def _init_common_modules(self):
        super(Search, self)._init_common_modules()
        self.spellchecker = SpellcheckOptions()

    def spellcheck(self, **kw):
        newself = self.clone()
        spellchecker = newself.spellchecker
        query = kw.get('q', '')
        if isinstance(query, unicode):
            kw['q'] = query.encode('utf-8')
        spellchecker.update(**kw)
        return newself
