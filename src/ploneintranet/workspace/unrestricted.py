"""
Perform some operations with enhanced access. Based on:
http://docs.plone.org/develop/plone/security/permissions.html#bypassing-permission-checks
"""  # noqa
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import (newSecurityManager,
                                              setSecurityManager)
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from plone import api


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def execute_as_manager(function, *args, **kwargs):
    """ Execute code under special role privileges.

    Example how to call::

        execute_as_manager(
            doSomeNormallyNotAllowedStuff,
            source_folder, target_folder)


    @param function: Method to be called with special privileges

    @param args: Passed to the function

    @param kwargs: Passed to the function
    """

    portal = api.portal.get()
    sm = getSecurityManager()

    try:
        # Clone the current user and assign a new role.
        # Note that the username (getId()) is left in exception
        # tracebacks in the error_log,
        # so it is an important thing to store.
        tmp_user = UnrestrictedUser(
            sm.getUser().getId(), '', ['Manager'], ''
        )

        # Wrap the user in the acquisition context of the portal
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)

        # Call the function
        return function(*args, **kwargs)

    except:
        # If special exception handlers are needed, run them here
        raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)
