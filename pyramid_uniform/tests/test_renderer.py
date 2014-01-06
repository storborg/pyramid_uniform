from unittest import TestCase

from pyramid.testing import DummyRequest

from .. import (Form, FormRenderer,
                FormNotValidatedError, FormInvalid,
                csrf_field)

from .utils import DummySchema, DummyObject, dummy_csrf_token


class TestRenderer(TestCase):

    def test_success_has_empty_errorlist(self):
        request = DummyRequest(post={'foo': 'hello'})
        form = Form(request, DummySchema())
        self.assertTrue(form.validate(skip_csrf=True))

        renderer = FormRenderer(form)
        self.assertEqual(renderer.errorlist('foo'), '')

    def test_failure_has_errorlist(self):
        request = DummyRequest(post={'foo': ''})
        form = Form(request, DummySchema())
        self.assertFalse(form.validate(skip_csrf=True))

        renderer = FormRenderer(form)
        self.assertIn('enter a value', renderer.errorlist('foo'))

    def _make_renderer(self, value='hello'):
        request = DummyRequest(post={'foo': value})
        form = Form(request, DummySchema())
        form.validate(skip_csrf=True)
        return FormRenderer(form)

    def test_value(self):
        renderer = self._make_renderer()
        self.assertEqual(renderer.value('foo'), 'hello')

    def test_text_without_param(self):
        renderer = self._make_renderer()
        tag = renderer.text('bar', 'somevalue')
        self.assertIn('<input', tag)
        self.assertIn('bar', tag)
        self.assertIn('somevalue', tag)

    def test_text_with_param(self):
        renderer = self._make_renderer()
        tag = renderer.text('foo', 'somevalue')
        self.assertIn('<input', tag)
        self.assertIn('foo', tag)
        self.assertIn('hello', tag)
        self.assertNotIn('somevalue', tag)

    def test_file(self):
        renderer = self._make_renderer()
        tag = renderer.file('hello')
        self.assertIn('<input', tag)
        # XXX

    def test_hidden(self):
        renderer = self._make_renderer()
        tag = renderer.hidden('hello')
        self.assertIn('<input', tag)
        # XXX

    def test_radio(self):
        renderer = self._make_renderer()
        tag = renderer.radio('hello')
        self.assertIn('<input', tag)
        # XXX

    def test_submit(self):
        renderer = self._make_renderer()
        tag = renderer.submit('hello')
        self.assertIn('<input', tag)
        # XXX

    def test_select(self):
        renderer = self._make_renderer()
        tag = renderer.select('hello', [('a', 12), ('b', 24)], None)
        self.assertIn('<select', tag)
        # XXX

    def test_checkbox(self):
        renderer = self._make_renderer()
        tag = renderer.checkbox('hello')
        # XXX

    def test_textarea(self):
        renderer = self._make_renderer()
        tag = renderer.textarea('hello')
        # XXX

    def test_password(self):
        renderer = self._make_renderer()
        tag = renderer.password('hello')
        # XXX

    def test_is_error(self):
        renderer = self._make_renderer('')
        self.assertTrue(renderer.is_error('foo'))

        renderer = self._make_renderer('hello')
        self.assertFalse(renderer.is_error('foo'))

    def test_errors_for(self):
        renderer = self._make_renderer('')
        errors = renderer.errors_for('foo')
        self.assertEqual(len(errors), 1)
        self.assertIn('enter a value', errors[0])

        renderer = self._make_renderer('hello')
        self.assertEqual(renderer.errors_for('foo'), [])

    def test_begin(self):
        renderer = self._make_renderer()
        tag = renderer.begin()
        self.assertIn('<form', tag)

    def test_end(self):
        renderer = self._make_renderer()
        tag = renderer.end()
        self.assertEqual(tag, '</form>')

    def test_csrf(self):
        renderer = self._make_renderer()
        tag = renderer.csrf()
        self.assertNotIn('div', tag)
        self.assertIn('<input', tag)
        self.assertIn(dummy_csrf_token, tag)

    def test_csrf_token(self):
        renderer = self._make_renderer()
        tag = renderer.csrf_token()
        self.assertIn('<input', tag)
        self.assertIn('<div', tag)
        self.assertIn(dummy_csrf_token, tag)

    def test_explicit_id(self):
        renderer = self._make_renderer()
        tag = renderer.text('foo', id='tiger')
        self.assertIn('id="tiger"', tag)

    def test_id_prefix(self):
        request = DummyRequest(post={'foo': 'hello'})
        form = Form(request, DummySchema())
        form.validate(skip_csrf=True)
        renderer = FormRenderer(form, id_prefix='blorg-')
        tag = renderer.text('foo')
        self.assertIn('id="blorg-foo"', tag)
