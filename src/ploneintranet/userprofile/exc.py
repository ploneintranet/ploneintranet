# -*- coding: utf-8 -*-
from zope import schema


class UserProfileParseError(Exception):
    """Base exception to add further information regarding which row, column
    at which an exception was raised in the csv import.
    """
    def __init__(self, message, details=None):
        super(UserProfileParseError, self).__init__(message)
        self.details = details


class RequiredMissing(schema.interfaces.RequiredMissing,
                      UserProfileParseError):
    """Override for schema.interfaces.RequiredMissing"""


class ConstraintNotSatisfied(schema.interfaces.ConstraintNotSatisfied,
                             UserProfileParseError):
    """Override for schema.interfaces.ConstraintNotSatisfied"""


class WrongType(schema.interfaces.WrongType,
                UserProfileParseError):
    """Override for schema.interfaces.WrongType"""


class MissingCoreFields(UserProfileParseError):
    """missing core require fields"""


class ExtraneousFields(UserProfileParseError):
    """extraneous fields found in csv"""


class DuplicateUser(UserProfileParseError):
    """User already exists"""
