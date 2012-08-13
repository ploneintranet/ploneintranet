def importVarious(context):

    if context.readDataFile('plonesocial.suite_various.txt') is None:
        return

    site = context.getSite()
    site.layout = "stream"
    site.default_page = "stream"
