# -*- coding: utf-8 -*-
from mock import patch
from plone import api
from ploneintranet import api as pi_api
from ploneintranet.search.testing import IntegrationTestCase

PROJECTNAME = 'ploneintranet.search'


class FakeCurrentUser(object):
    ''' This mocks a membrane user ofr out tests
    '''


class TestSearchOptionsPersistent(IntegrationTestCase):

    def setUp(self):
        super(TestSearchOptionsPersistent, self).setUp()
        self.portal = self.layer['portal']
        api.portal.set_registry_record(
            'ploneintranet.search.ui.persistent_options',
            True,
        )

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
