from formencode import ForEach, Schema, NestedVariables, validators
from pyramid.testing import DummySession


# This always stays the same.
dummy_csrf_token = DummySession().get_csrf_token()


class DummySchema(Schema):
    allow_extra_fields = False
    foo = validators.String(not_empty=True)


class LooseDummySchema(DummySchema):
    allow_extra_fields = True


class DummyObject(object):
    pass


class NestedDummySchema(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables]
    items = ForEach(DummySchema)
    subfields = DummySchema
    name = validators.String(not_empty=True)
    qty = validators.Int(min=4, max=100)
