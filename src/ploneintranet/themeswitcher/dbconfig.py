"""
This module enables you to configure your Plone site's registry for
ploneintranet.themeswitcher via buildout.
Just add something like the following under the [instance] section of your
buildout (i.e where you configure your plone instance):
zope-conf-additional +=
    <product-config ploneintranet.themeswitcher>
        instance_name ploneintranet
    </product-config>

WARNING: If you put the above in your buildout.cfg, your plone.registry entries
will be overridden with those values every time you restart your zope server.
In other words, you basically lose the ability to configure your themeswitcher
settings via Plone itself.
"""
from App.config import getConfiguration
from plone.registry.interfaces import IRegistry
from ploneintranet.themeswitcher.interfaces import IThemeSwitcherSettings
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility

import Zope2
import logging
import transaction


configuration = getConfiguration()
if not hasattr(configuration, 'product_config'):
    conf = None
else:
    conf = configuration.product_config.get('ploneintranet.themeswitcher')


log = logging.getLogger(__name__)


def dbconfig(event):
    """
    Override the themeswitching registry config with buildout product_config,
    when it is available
    """
    if conf is None:
        log.info('No product config found. Configuration will not be set')
        return

    db = Zope2.DB
    connection = db.open()
    root_folder = connection.root().get(ZopePublication.root_name, None)
    instance_name = conf.get('instance_name')
    if not instance_name:
        log.error(
            '"instance_name" needs to be set if you want to configure '
            'ploneintranet.themeswitcher from buildout.'
        )
        return

    plone = root_folder.get(instance_name)
    if plone is None:
        log.error('No Plone instance with instance_name "%s" found.'
                  % instance_name)
        return

    registry = getUtility(IRegistry, context=plone)
    settings = registry.forInterface(IThemeSwitcherSettings, check=False)
    if conf.get('hostname_switchlist'):
        try:
            settings.hostname_switchlist = [
                unicode(conf.get('hostname_switchlist')), ]
            log.info('hostname_switchlist configured')
        except AttributeError as e:
            log.exception(e)
            log.error('Could not configure hostname_switchlist. Is '
                      'PloneIntranet installed?')
    transaction.commit()
