
def read_token(request):
    """Read a GCM registration token from the request.

    :returns: The token.
    :rtype: str
    :raises: ValueError (if token cannot be obtained)
    """
    token = request.form.get('token')
    if token is None:
        raise ValueError('bad token')
    elif isinstance(token, unicode):
        return token.encode('ascii')
    return token
