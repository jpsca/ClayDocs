class claydocsException(Exception):
    pass


class InvalidFrontMatter(claydocsException):
    pass


class InvalidNav(claydocsException):
    pass


class Abort(claydocsException):
    pass
