from plone import api


def demo(context):

    if context.readDataFile('ploneintranet.suite_demo.txt') is None:
        return

    portal = api.portal.get()

    # see: https://github.com/cosent/plonesocial.suite/
    #       blob/master/src/plonesocial/suite/setuphandlers.py

    # for creating users and network

    # news item
    if 'news' in portal.keys():

        newscontent = [
            {'title': 'Second Indian Airline to join Global Airline Alliance',
             'description': 'Weak network in growing Indian aviation market'},

            {'title': 'BNB and Randomize to codeshare',
             'description': 'Starting September 10, BNB passengers will be' +
             'able to book connecting flights on Ethiopian Airlines.'},

            {'title': 'Alliance Officially Opens New Lounge',
             'description': ''},
        ]
        for newsitem in newscontent:
            api.content.create(
                type='News Item',
                title=newsitem['title'],
                description=newsitem['description'],
                container=portal['news'])
