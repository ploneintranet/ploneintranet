# coding=utf-8
from ploneintranet.calendar.setuphandlers import create_calendar_app
from ploneintranet.layout.upgrades.to0005 import add_apps


def add_calendar_app(context):
    add_apps(context)
    create_calendar_app()
