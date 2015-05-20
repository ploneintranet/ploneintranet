import responses

from ..testing import IntegrationTestCase
from ..tasks import generate_and_add_preview, PreviewGenerationException


class TestAsyncTasks(IntegrationTestCase):
    def setUp(self):
        super(TestAsyncTasks, self).setUp()

    @responses.activate
    def tearDown(self):
        super(TestAsyncTasks, self).tearDown()
        responses.reset()

    @responses.activate
    def test_generate_preview_success(self):
        """
        Test that a 200 response doesn't raise
        """
        responses.add(
            responses.GET,
            'http://localhost:8000/@@generate-preview',
            body='',
            status=200)
        generate_and_add_preview(
            'http://localhost:1234/path/to/obj',
            {'__ac': 'ABC123'}
        )

    @responses.activate
    def test_generate_preview_failure(self):
        """
        Test that a 403 response raises
        """
        responses.add(responses.GET,
                      'http://localhost:8000/@@generate-preview',
                      body='',
                      status=403,
                      )
        with self.assertRaises(PreviewGenerationException):
            generate_and_add_preview(
                'http://localhost:1234/path/to/obj',
                {'__ac': 'ABC123'}
            )
