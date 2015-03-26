from datetime import datetime
from persistent import Persistent


class ContentAction(Persistent):
    """
    Definition of a ContentAction object

    This is what will be stored for each user with details of
    actions on content that the user has been tasked with

    :ivar userid: (`str`) The userid this action belongs to
    :ivar content_uid: (`str`) The UID of the content
    :ivar verb: (`str`) The verb of the action to be taken
    :ivar created: (`datetime`) The datetime this action was created
    :ivar completed: (`datetime`) The datetime this action was completed
    """
    def __init__(self, userid, content_uid, verb, created=None,
                 completed=None):
        self.userid = userid
        self.content_uid = content_uid
        self.verb = verb
        if created is None:
            self.created = datetime.now()
        else:
            self.created = created
        self.completed = completed
        self.modified = None

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def latest_date(self):
        if self.modified is None:
            return self.created
        return self.modified

    def mark_complete(self):
        """
        Mark this ContentAction as complete
        """
        self.completed = datetime.now()
