from unittest import TestCase

from formencode import Invalid
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.testing import DummyRequest

from .. import (Form,
                FormNotValidatedError, FormInvalid,
                csrf_field)

from .utils import DummySchema, DummyObject, dummy_csrf_token


class TestForm(TestCase):

    def test_validate_success(self):
        request = DummyRequest(post={'foo': 'hello'})
        form = Form(request, DummySchema())
        self.assertTrue(form.validate(skip_csrf=True))

    def test_validate_failure(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        self.assertFalse(form.validate(skip_csrf=True))

        self.assertIn('foo', form.errors)

    def test_validate_get(self):
        request = DummyRequest(params={'foo': 'hello'})
        form = Form(request, DummySchema(), method='GET')
        self.assertTrue(form.validate(skip_csrf=True))

    def test_validate_twice(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        self.assertFalse(form.validate(skip_csrf=True))
        self.assertFalse(form.validate(skip_csrf=True))

        self.assertIn('foo', form.errors)

    def test_invalid_non_error_dict(self):
        request = DummyRequest(post={'what': ''})
        form = Form(request, DummySchema())
        with self.assertRaises(Invalid) as cm:
            form.validate(skip_csrf=True)

    def test_validate_csrf(self):
        request = DummyRequest(post={
            'foo': 'hello',
            csrf_field: dummy_csrf_token
        })
        form = Form(request, DummySchema())
        self.assertTrue(form.validate())

    def test_validate_method_get_not_allowed(self):
        request = DummyRequest(params={'foo': ''})
        form = Form(request, DummySchema())
        self.assertFalse(form.validate(skip_csrf=True))

    def test_assert_valid(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        with self.assertRaises(AssertionError) as cm:
            form.assert_valid(skip_csrf=True)
        exc = cm.exception
        self.assertIn('foo', str(exc))

    def test_bind(self):
        request = DummyRequest(post={'foo': 'quux'})
        form = Form(request, DummySchema())
        self.assertTrue(form.validate(skip_csrf=True))

        obj = DummyObject()
        form.bind(obj)
        self.assertEqual(obj.foo, 'quux')

    def test_bind_without_validating(self):
        request = DummyRequest(post={'foo': 'quux'})
        form = Form(request, DummySchema())

        obj = DummyObject()
        with self.assertRaises(FormNotValidatedError):
            form.bind(obj)

    def test_bind_invalid(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        self.assertFalse(form.validate(skip_csrf=True))

        obj = DummyObject()
        with self.assertRaises(FormInvalid):
            form.bind(obj)

    def test_errors_for(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        self.assertFalse(form.validate(skip_csrf=True))

        errors = form.errors_for('foo')
        self.assertEqual(len(errors), 1)
        self.assertIn('enter a value', errors[0])

    def test_is_error(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        self.assertFalse(form.validate(skip_csrf=True))

        self.assertTrue(form.is_error('foo'))

    def test_method_allowed_implicit_method(self):
        request = DummyRequest(method='GET')
        form = Form(request, DummySchema(), method=None)
        self.assertTrue(form.method_allowed)

        request = DummyRequest(method='POST')
        form = Form(request, DummySchema(), method=None)
        self.assertTrue(form.method_allowed)

    def test_method_allowed_explicit_method(self):
        request = DummyRequest(method='GET')
        form = Form(request, DummySchema(), method='POST')
        self.assertFalse(form.method_allowed)

        request = DummyRequest(method='POST')
        form = Form(request, DummySchema(), method='POST')
        self.assertTrue(form.method_allowed)

    def test_validate_csrf_missing(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        with self.assertRaises(HTTPBadRequest):
            form.validate_csrf()

    def test_validate_csrf_wrong(self):
        request = DummyRequest(post={'foo': '', csrf_field: 'wrong'})
        form = Form(request, DummySchema())
        with self.assertRaises(HTTPBadRequest):
            form.validate_csrf()


