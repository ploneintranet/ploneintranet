# coding=utf-8
from AccessControl import Unauthorized
from Products.Five.browser import BrowserView


class View(BrowserView):
    ''' Always raise Unauthorized
    '''
    def __call__(self):
        raise Unauthorized('This is a test')
