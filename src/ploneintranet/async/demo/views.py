from Products.Five import BrowserView
from celery.result import AsyncResult
from .tasks import create_content


class CreateContentView(BrowserView):

    def __call__(self):
        result = create_content.delay(
            self.context,
            'Document',
            'foo',
            setTitle=u"Foo",
            setDescription=u"Just a test page",
            setText=u"<p>Hello <em>world</em>!</p>"
        )
        self.request.response.redirect(
            self.context.absolute_url().rstrip('/') +
            ('/@@task_result?task_id=%s' % result.id)
        )


class TaskResultPoll(BrowserView):

    def __call__(self):
        result = AsyncResult(self.request.form['task_id'])
        self.request.response.setHeader('Content-Type', 'text/plain')
        if result.ready():
            return 'Done! Result is %s' % result.result
        else:
            return 'Still in progress, retry later!'
