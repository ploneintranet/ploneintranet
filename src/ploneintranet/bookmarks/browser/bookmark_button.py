# coding=utf-8
from plone.memoize.view import memoize
from ploneintranet.bookmarks.browser.base import BookmarkView
from ploneintranet.core import ploneintranetCoreMessageFactory as _


class BookmarkProfileView(BookmarkView):
    ''' A view that outputs a bookmark button in a form
    '''
    @property
    @memoize
    def is_bookmarked(self):
        ''' Check if an object is bookmarked by uid
        '''
        uid = self.context.UID
        if uid is None:
            uid = self.context.context.UID
        if callable(uid):
            uid = uid()
        return self.ploneintranet_network.is_bookmarked('content', uid)

    @property
    def button_options(self):
        ''' Get the link options
        '''
        if self.is_bookmarked:
            options = {
                'action': '@@unbookmark',
                'title': _('Click to remove this bookmark'),
                'css_class': 'icon-bookmark active ',
                'label': self.context.translate(_(
                    'bookmarked_button_label',
                    default=u'<strong>Bookmarked</strong>',
                ))
            }
        else:
            options = {
                'action': '@@bookmark',
                'title': self.context.translate(
                    _(
                        'unbookmarked_button_label',
                        default=u'Click to bookmark the profile page of ${fullname}',  # noqa
                        mapping={'fullname': self.context.fullname},
                    )
                ),
                'css_class': 'icon-bookmark-empty',
                'label': _('<strong>Bookmark</strong> this page'),
            }
        return options
