import urlparse
import responses

from ..testing import IntegrationTestCase
from ..celerytasks import generate_and_add_preview, PreviewGenerationException


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
            responses.POST,
            'http://localhost:1234/path/to/obj/@@generate-previews',
            body='',
            status=200
        )
        generate_and_add_preview(
            'http://localhost:1234/path/to/obj',
            {'__ac': 'ABC123'}
        )

    @responses.activate
    def test_generate_preview_failure(self):
        """
        Test that a 403 response raises
        """
        responses.add(
            responses.POST,
            'http://localhost:1234/path/to/obj/@@generate-previews',
            body='',
            status=403,
        )
        with self.assertRaises(PreviewGenerationException):
            generate_and_add_preview(
                'http://localhost:1234/path/to/obj',
                {'__ac': 'ABC123'}
            )

    @responses.activate
    def test_generate_preview_params(self):
        """
        Test that a 403 response raises
        """
        def request_callback(request):
            self.assertIn('__ac', request._cookies)
            data = urlparse.parse_qs(request.body)
            self.assertEqual(data['action'][0], 'add')
            self.assertEqual(
                data['url'][0],
                'http://localhost:1234/path/to/obj'
            )
            return (200, {}, '')

        responses.add_callback(
            responses.POST,
            'http://localhost:1234/path/to/obj/@@generate-previews',
            callback=request_callback
        )
        generate_and_add_preview(
            'http://localhost:1234/path/to/obj',
            {'__ac': 'ABC123'}
        )
