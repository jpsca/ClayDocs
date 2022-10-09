class ClayDocsException(Exception):
    pass


class InvalidFrontMatter(ClayDocsException):
    pass


class InvalidNav(ClayDocsException):
    pass


class Abort(ClayDocsException):
    pass