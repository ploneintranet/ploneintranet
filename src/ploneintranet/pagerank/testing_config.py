# test config outside of test modules
# to avoid dependency errors when running 'normal' site

EDGE_WEIGHTS = {'social_following': 2,
                'content_tree': 1,
                'content_authors': 3,
                'content_tags': 4}

SOCIAL_GRAPH = set([('admin', 'allan_neece'), ('admin', 'dollie_nocera'), ('admin', 'esmeralda_claassen'), ('admin', 'jesse_shaikh'), ('allan_neece', 'dollie_nocera'), ('allan_neece', 'esmeralda_claassen'), ('allan_neece', 'jamie_jacko'), ('allan_neece', 'pearlie_whitby'), ('christian_gast', 'guy_hachey'), ('christian_gast', 'lance_stockstill'), ('christian_gast', 'pearlie_whitby'), ('christian_gast', 'rosalinda_roache'), ('christian_stoner', 'clare_presler'), ('clayton_primavera', 'christian_gast'), ('clayton_primavera', 'christian_stoney'), ('clayton_primavera', 'fernando_poulter'), ('clayton_primavera', 'lance_stockstill'), ('clayton_primavera', 'neil_wichmann'), ('dollie_nocera', 'allan_neece'), ('dollie_nocera', 'esmeralda_claassen'), ('dollie_nocera', 'jamie_jacko'), ('esmeralda_claassen', 'jamie_sylvest'), ('esmeralda_claassen', 'jesse_shaikh'), ('esmeralda_claassen', 'lance_stockstill'), ('esmeralda_claassen', 'neil_wichmann'), ('fernando_poulter', 'admin'), ('fernando_poulter', 'christian_stoney'), ('fernando_poulter', 'jesse_shaikh'), ('fernando_poulter', 'lance_stockstill'), ('fernando_poulter', 'neil_wichmann'), ('guy_hachey', 'admin'), ('guy_hachey', 'clare_presler'), ('guy_hachey', 'clayton_primavera'), ('guy_hachey', 'dollie_nocera'), ('guy_hachey', 'fernando_poulter'), ('guy_hachey', 'lance_stockstill'), ('guy_hachey', 'rosalinda_roache'), ('jamie_jacko', 'clare_presler'), ('jamie_jacko', 'clayton_primavera'), ('jamie_jacko', 'lance_stockstill'), ('jamie_jacko', 'neil_wichmann'), ('jamie_jacko', 'rosalinda_roache'), ('jamie_sylvest', 'esmeralda_claassen'), ('jamie_sylvest', 'fernando_poulter'), ('jamie_sylvest', 'lance_stockstill'), ('jamie_sylvest', 'pearlie_whitby'), ('jesse_shaikh', 'esmeralda_claassen'), ('jesse_shaikh', 'fernando_poulter'), ('jesse_shaikh', 'pearlie_whitby'), ('kurt_silvio', 'clare_presler'), ('lance_stockstill', 'allan_neece'), ('lance_stockstill', 'neil_wichmann'), ('lance_stockstill', 'pearlie_whitby'), ('neil_wichmann', 'allan_neece'), ('neil_wichmann', 'christian_stoney'), ('neil_wichmann', 'jesse_shaikh'), ('pearlie_whitby', 'jamie_jacko'), ('pearlie_whitby', 'lance_stockstill'), ('rosalinda_roache', 'admin'), ('rosalinda_roache', 'dollie_nocera'), ('rosalinda_roache', 'jamie_sylvest'), ('rosalinda_roache', 'jesse_shaikh')])  # flake8:noqa


CONTENT_TAGS = set([('path:/plone/public/d1', 'tag:foo'),
                    ('path:/plone/public/d1', 'tag:nix'),
                    ('tag:nix', 'path:/plone/public/d1'),
                    ('tag:foo', 'path:/plone/public/d1'),
                    ('tag:bar', 'path:/plone/public'),
                    ('tag:foo', 'path:/plone/public'),
                    ('path:/plone/public', 'tag:foo'),
                    ('path:/plone/public', 'tag:bar')])
