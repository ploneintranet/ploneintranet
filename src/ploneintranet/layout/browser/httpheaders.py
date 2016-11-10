from plone.app.layout.viewlets.httpheaders import HTTPCachingHeaders


class HTTPHeaders(HTTPCachingHeaders):
    """ Simple Wrapper to set http headers for standalone views """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.update()
