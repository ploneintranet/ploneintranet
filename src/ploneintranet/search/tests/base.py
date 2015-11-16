import abc


class SiteSearchTestBaseMixin(object):
    """Protocol for implementator to provide the object under test."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _make_utility(self, *args, **kw):
        """Return the utility under test."""

    def _record_debug_info(self, query_response):
        """This is a hook that allows sub-classes to record query responses.

        Useful for debugging tests.
        """

    def _query(self, util, *args, **kw):
        response = util.query(*args, **kw)
        self._record_debug_info(response)
        return response
