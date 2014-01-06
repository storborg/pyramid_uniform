from formencode import Schema, validators
from pyramid.testing import DummySession


# This always stays the same.
dummy_csrf_token = DummySession().get_csrf_token()


class DummySchema(Schema):
    allow_extra_fields = False
    foo = validators.String(not_empty=True)


class DummyObject(object):
    pass
