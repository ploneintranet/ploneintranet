# -*- coding: utf-8 -*-
from mock import patch
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.search.testing import IntegrationTestCase

import locale

PROJECTNAME = 'ploneintranet.search'


class FakeCurrentUser(object):
    ''' This mocks a membrane user ofr out tests
    '''


class BaseSearchTestCase(IntegrationTestCase):
    ''' Base test case we need to test the views
    '''
    def setUp(self):
        super(BaseSearchTestCase, self).setUp()
        self.portal = self.layer['portal']

    def get_search_view(self, params={}):
        ''' Return the search view called with params
        '''
        request = self.layer['request'].clone()
        request.form.update(params)
        return api.content.get_view(
            'search',
            self.portal,
            request,
        )


class TestSearchView(BaseSearchTestCase):
    ''' Test search view functionality
    '''

    def test_sorting_method(self):
        ''' The function we use for sorting items that have a title
        '''
        view = self.get_search_view()
        old_locale = locale.getlocale(locale.LC_COLLATE)
        # make the tests indipendent from the environment
        locale.setlocale(locale.LC_COLLATE, ('en_US', 'UTF-8'))
        items = [
            {'title': u'A'},
            {'title': u'B'},
            {'title': u'c'},
            {'title': u'sr'},
            {'title': u'st'},
            {'title': u'z'},
            {'title': u'ß'},
            {'title': u'à'},
            {'title': u'ä'},
        ]
        self.assertListEqual(
            sorted(items, cmp=view.cmp_item_title),
            [
                {'title': u'A'},
                {'title': u'à'},
                {'title': u'ä'},
                {'title': u'B'},
                {'title': u'c'},
                {'title': u'sr'},
                {'title': u'ß'},
                {'title': u'st'},
                {'title': u'z'},
            ]
        )
        # reset the locale
        locale.setlocale(locale.LC_COLLATE, old_locale)


class TestSearchOptionsPersistent(BaseSearchTestCase):

    def setUp(self):
        super(TestSearchOptionsPersistent, self).setUp()
        api.portal.set_registry_record(
            'ploneintranet.search.ui.persistent_options',
            True,
        )

    def test_defaults_not_modified_vanilla(self):
        ''' If the user accepts the defaults, we are not storing anything on it
        '''
        with patch(
            'ploneintranet.api.userprofile.get_current',
            return_value=FakeCurrentUser(),
        ):
            user = pi_api.userprofile.get_current()
            view = self.get_search_view()
            self.assertEqual(view.display_previews(), True)
            self.assertEqual(view.get_sorting(), None)
            self.assertFalse(hasattr(user, 'display_previews'))
            self.assertFalse(hasattr(user, 'search_sorting'))

    def test_options_persist(self):
        ''' If the user accepts the defaults, we are not storing anything on it
        '''
        with patch(
            'ploneintranet.api.userprofile.get_current',
            return_value=FakeCurrentUser(),
        ):
            user = pi_api.userprofile.get_current()
            # First we call the view with non default parameter
            view = self.get_search_view({
                'SearchableText_filtered': 'x',
                'display-previews': 'off',
                'results-sorting': 'date',
            })
            self.assertFalse(view.display_previews(), False)
            self.assertEqual(view.get_sorting(), '-created')
            self.assertEqual(user.display_previews, 'off')
            self.assertEqual(user.search_sorting, 'date')

            # Then with no parameters and see that the options persist
            view = self.get_search_view()
            self.assertFalse(view.display_previews(), False)
            self.assertEqual(view.get_sorting(), '-created')
            self.assertEqual(user.display_previews, 'off')
            self.assertEqual(user.search_sorting, 'date')

        # If we change use we have the default options
        with patch(
            'ploneintranet.api.userprofile.get_current',
            return_value=FakeCurrentUser(),
        ):
            user = pi_api.userprofile.get_current()
            view = self.get_search_view()
            self.assertEqual(view.display_previews(), True)
            self.assertEqual(view.get_sorting(), None)
            self.assertFalse(hasattr(user, 'display_previews'))
            self.assertFalse(hasattr(user, 'search_sorting'))

            # But we can manipulate them opertaing on the user
            user.display_previews = 'off'
            user.search_sorting = 'date'
            view = self.get_search_view()
            self.assertFalse(view.display_previews(), False)
            self.assertEqual(view.get_sorting(), '-created')
            self.assertEqual(user.display_previews, 'off')
            self.assertEqual(user.search_sorting, 'date')

    def tearDown(self):
        super(TestSearchOptionsPersistent, self).tearDown()
        api.portal.set_registry_record(
            'ploneintranet.search.ui.persistent_options',
            False,
        )
