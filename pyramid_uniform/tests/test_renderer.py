from unittest import TestCase

from pyramid.testing import DummyRequest

from .. import Form, FormRenderer, csrf_field

from .utils import DummySchema, dummy_csrf_token


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

    def test_text_without_id(self):
        renderer = self._make_renderer()
        tag = renderer.text('foo', 'somevalue', id=None)
        self.assertEqual(tag,
                         '<input name="foo" type="text" value="hello" />')

    def test_file(self):
        renderer = self._make_renderer()
        tag = renderer.file('hello')
        self.assertEqual(tag,
                         '<input id="hello" name="hello" type="file" />')

    def test_hidden(self):
        renderer = self._make_renderer()
        tag = renderer.hidden('hello')
        self.assertEqual(tag,
                         '<input id="hello" name="hello" type="hidden" />')

    def test_radio(self):
        renderer = self._make_renderer()
        tag = renderer.radio('hello', 'a')
        self.assertEqual(
            tag,
            '<input id="hello_a" name="hello" type="radio" value="a" />')

    def test_radio_selected(self):
        renderer = self._make_renderer()
        tag = renderer.radio('hello', 'b', checked=True)
        self.assertEqual(
            tag,
            '<input checked="checked" id="hello_b" '
            'name="hello" type="radio" value="b" />')

    def test_submit(self):
        renderer = self._make_renderer()
        tag = renderer.submit('hello')
        self.assertEqual(
            tag,
            '<input id="hello" name="hello" type="submit" />')

    def test_select(self):
        renderer = self._make_renderer()
        tag = renderer.select('hello', None, [('a', 12), ('b', 24)])
        self.assertEqual(
            tag,
            '<select id="hello" name="hello">\n'
            '<option value="a">12</option>\n'
            '<option value="b">24</option>\n'
            '</select>')

    def test_select_scalar_selected(self):
        renderer = self._make_renderer()
        tag = renderer.select('hello', 'a', [('a', 12), ('b', 24)])
        self.assertEqual(
            tag,
            '<select id="hello" name="hello">\n'
            '<option selected="selected" value="a">12</option>\n'
            '<option value="b">24</option>\n'
            '</select>')

    def test_select_multiple(self):
        renderer = self._make_renderer()
        tag = renderer.select('hello', 'a', [('a', 12), ('b', 24)])
        self.assertEqual(
            tag,
            '<select id="hello" name="hello">\n'
            '<option selected="selected" value="a">12</option>\n'
            '<option value="b">24</option>\n'
            '</select>')

    def test_select_list_selected(self):
        renderer = self._make_renderer()
        tag = renderer.select('hello', ['a', 'b'], [('a', 12), ('b', 24)])
        self.assertEqual(
            tag,
            '<select id="hello" name="hello">\n'
            '<option selected="selected" value="a">12</option>\n'
            '<option selected="selected" value="b">24</option>\n'
            '</select>')

    def test_checkbox(self):
        renderer = self._make_renderer()
        tag = renderer.checkbox('hello')
        self.assertEqual(
            tag,
            '<input id="hello" name="hello" type="checkbox" value="1" />')

    def test_checkbox_checked(self):
        renderer = self._make_renderer()
        tag = renderer.checkbox('hello', checked=True)
        self.assertEqual(
            tag,
            '<input checked="checked" id="hello" '
            'name="hello" type="checkbox" value="1" />')

    def test_textarea(self):
        renderer = self._make_renderer()
        tag = renderer.textarea('hello')
        self.assertEqual(
            tag,
            '<textarea id="hello" name="hello"></textarea>')

    def test_password(self):
        renderer = self._make_renderer()
        tag = renderer.password('hello')
        self.assertEqual(
            tag,
            '<input id="hello" name="hello" type="password" />')

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
        self.assertIn(dummy_csrf_token, tag)

    def test_begin_skip_csrf(self):
        renderer = self._make_renderer()
        tag = renderer.begin(skip_csrf=True)
        self.assertIn('<form', tag)
        self.assertNotIn(dummy_csrf_token, tag)

    def test_form_skip_csrf(self):
        request = DummyRequest(post={'foo': 'hello'})
        form = Form(request, DummySchema(), skip_csrf=True)
        form.validate(skip_csrf=True)
        renderer = FormRenderer(form)
        tag = renderer.begin()
        self.assertIn('<form', tag)
        self.assertNotIn(dummy_csrf_token, tag)

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
        self.assertIn(csrf_field, tag)

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

    def test_renderer_unvalidated_form(self):
        request = DummyRequest()
        form = Form(request, DummySchema())
        renderer = FormRenderer(form)
        tag = renderer.text('hello')
        self.assertEqual(
            tag,
            '<input id="hello" name="hello" type="text" />')

    def test_name_prefix(self):
        request = DummyRequest(post={'foo': 'hello'})
        form = Form(request, DummySchema())
        renderer = FormRenderer(form, name_prefix='partial.')
        tag = renderer.text('foo')
        self.assertIn('name="partial.foo"', tag)

    def test_name_prefix_id_generation(self):
        request = DummyRequest(post={'foo': 'hello'})
        form = Form(request, DummySchema())
        renderer = FormRenderer(form, name_prefix='partial.')
        tag = renderer.text('foo')
        self.assertIn('name="partial.foo"', tag)
        self.assertIn('id="partial_foo', tag)

    def test_none_name(self):
        renderer = self._make_renderer()
        tag = renderer.text(None, 'somevalue')
        self.assertIn('<input', tag)
        self.assertNotIn('name="', tag)
        self.assertIn('somevalue', tag)
