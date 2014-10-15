class ServerError(Exception):
    """ A problem has occured in communication with the Docconv server """


class ConfigError(Exception):
    """ A problem in the configuration prevents completing the current task """
