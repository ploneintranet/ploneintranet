def importVarious(context):

    if context.readDataFile('plonesocial.suite_various.txt') is None:
        return

    site = context.getSite()
    site.layout = "activitystream_portal"
    site.default_page = "activitystream_portal"
