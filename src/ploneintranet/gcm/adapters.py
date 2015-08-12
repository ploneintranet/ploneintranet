

class Message(object):

    def __init__(self, context):
        self.context = context

    def __json__(self):
        return vars(self.context)
