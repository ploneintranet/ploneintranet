import json
from Products.Five import BrowserView

from ..behaviors import ITodo

class UpdateTodoStatus(BrowserView):

    def __call__(self):
        status = self.request.get("status")
        if not status:
            result = {'error': 'no status'}
        else:
            todo = ITodo(self.context)
            todo.status = status
            result = {'success': True, 'status': status}

        self.request.response.setHeader('Content-type', 'application/json')
        return json.dumps(result)
