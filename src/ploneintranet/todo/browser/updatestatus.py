import json
from Products.Five import BrowserView
from zope.security import checkPermission

from ..behaviors import ITodo


class UpdateTodoStatus(BrowserView):

    def update_status(self, status):
        if not checkPermission(
            'ploneintranet.todo: Change task status',
            self.context):
            return {'error': 'not allowed'}

        if not status:
            return {'error': 'no status'}

        todo = ITodo(self.context)
        todo.status = status
        return {'success': True, 'status': status}

    def __call__(self):
        status = self.request.get("status")
        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(self.update_status(status))
