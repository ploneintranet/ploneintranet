from plone import api


def demo(context):

    if context.readDataFile('ploneintranet.suite_demo.txt') is None:
        return

    portal = api.portal.get()

    # see: https://github.com/cosent/plonesocial.suite/
    #       blob/master/src/plonesocial/suite/setuphandlers.py

    # for creating users and network

    # news item
    api.content.create(
        type='News Item',
        title='Second Indian Airline to join Global Airline Alliance',
        description='Weak network in growing Indian aviation market',
        container=portal)
