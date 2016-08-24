# coding=utf-8
from ploneintranet.bookmarks.setuphandlers import create_bookmark_app
from ploneintranet.layout.upgrades.to0005 import add_apps


def add_bookmark_app(context):
    add_apps()
    create_bookmark_app()
