import logging

import six
from formencode import Invalid
from webhelpers2.html import tags
from webhelpers2.html.builder import HTML
from pyramid.httpexceptions import HTTPBadRequest


log = logging.getLogger('pyramid_uniform.validate')

csrf_field = "_authentication_token"


class FormError(Exception):
    """
    Superclass for form-related errors.
    """
    def __init__(self, *args, **kw):
        args = args or (self.message,)
        Exception.__init__(self, *args, **kw)


class FormNotValidatedError(FormError):
    """
    Raised when form data is used before form has been validated: for example,
    when ``form.bind()`` is called.
    """
    message = 'Form has not been validated; call validate() first'


class FormInvalid(FormError):
    """
    Raised when form data is used but the form is not valid.
    """
    message = 'Form is invalid'


class State(object):
    """
    A relatively simple state object for FormEncode to use, with a reference to
    the request being validated.
    """
    def __init__(self, request):
        self.request = request


class Form(object):

    def __init__(self, request, schema, method='POST'):
        self.request = request
        self.schema = schema
        self.method = method
        self.dict_char = '.'
        self.list_char = '-'
        self.multipart = True
        self.is_validated = False
        self.errors = {}
        self.data = {}
        self.state = State(request)

    @property
    def method_allowed(self):
        """Is the method that was used to submit this form allowed?.

        If this form doesn't have a request method set (i.e., if it was
        explicitly set to ``None``), any method is valid. Otherwise, the
        method of the form submission must match the method required by this
        form.

        """
        if self.method:
            return self.request.method == self.method
        return True

    def validate(self, skip_csrf=False, assert_valid=False):
        """Validate a form submission.

        When ``assert_valid`` is ``False`` (the default), a bool will be
        returned to indicate whether the form was valid. (Note: this isn't
        strictly true--a missing or bad CSRF token will result in a
        immediate ``400 Bad Request`` response).

        When ``assert_valid`` is ``True``, certain conditions will be
        ``assert``ed. When an assertion fails, the resulting
        ``AssertionError`` will cause an internal server error, which will
        in turn cause an error email to be sent out.

        """
        request = self.request
        if self.is_validated:
            return not self.errors

        if assert_valid:
            assert self.method_allowed, (
                'Expected request method {}; got {} instead'
                .format(self.method, self.request.method))
        elif not self.method_allowed:
            return False

        params = self._get_params()

        if not skip_csrf:
            self.validate_csrf(params)
            # Remove CSRF token from params; use a copy so the original
            # request params aren't changed.
            params = params.copy()
            params.pop(csrf_field)

        self.data.update(params)

        try:
            self.data = self.schema.to_python(params, self.state)
        except Invalid as e:
            if e.error_dict:
                self.errors = e.unpack_errors(
                    True, self.dict_char, self.list_char)
            else:
                # unpack_errors() will raise an AssertionError when the
                # Invalid exception does not contain an error dict. Since
                # that's not particularly helpful, re-raise the original
                # exception so we at least have some idea of what happened.
                raise e
            log.error("Validation failure on %r from %s [%s]\n"
                      "Params:\n%r\n\nErrors:\n%r\n",
                      request.url,
                      # Work with DummyRequest
                      getattr(request, 'remote_addr', None),
                      getattr(request, 'user_agent', None),
                      params, self.errors)

        self.is_validated = True
        valid = not self.errors

        if assert_valid:
            assert valid, "form invalid with errors: %r" % self.errors

        return valid

    def assert_valid(self, **kw):
        self.validate(assert_valid=True, **kw)

    def validate_csrf(self, params=None):
        if params is None:
            params = self._get_params()
        if csrf_field not in params:
            raise HTTPBadRequest('Missing CSRF token')
        got_token = params.get(csrf_field)
        wanted_token = self.request.session.get_csrf_token()
        if got_token != wanted_token:
            raise HTTPBadRequest('Bad CSRF token: wanted %r, got %r' %
                                 (wanted_token, got_token))

    def _get_params(self):
        if self.method == 'POST':
            return self.request.POST
        else:
            return self.request.params

    def bind(self, obj):
        if not self.is_validated:
            raise FormNotValidatedError
        if self.errors:
            raise FormInvalid('Form not valid; cannot bind')
        items = [(k, v) for k, v in self.data.items() if not k.startswith('_')]
        for k, v in items:
            setattr(obj, k, v)
        return obj

    def errors_for(self, field):
        errors = self.errors.get(field, [])
        if isinstance(errors, six.string_types):
            errors = [errors]
        return errors

    def is_error(self, field):
        return field in self.errors


class Renderer(object):
    def __init__(self, data, errors, id_prefix=None):
        self.data = data
        self.errors = errors
        self.id_prefix = id_prefix

    def text(self, name, value=None, id=None, **attrs):
        return tags.text(name,
                         self.value(name, value),
                         self._get_id(id, name),
                         **attrs)

    def file(self, name, value=None, id=None, **attrs):
        return tags.file(name,
                         self.value(name, value),
                         self._get_id(id, name),
                         **attrs)

    def hidden(self, name, value=None, id=None, **attrs):
        if value is None:
            value = self.value(name)

        return tags.hidden(name,
                           value,
                           self._get_id(id, name),
                           **attrs)

    def radio(self, name, value=None, checked=False, label=None, **attrs):
        checked = self.value(name) == value or checked
        return tags.radio(name, value, checked, label, **attrs)

    def submit(self, name, value=None, id=None, **attrs):
        return tags.submit(name,
                           self.value(name, value),
                           self._get_id(id, name),
                           **attrs)

    def select(self, name, selected_values, options, id=None, **attrs):
        val = self.value(name, selected_values)
        if not isinstance(val, list):
            val = [val]
        return tags.select(name,
                           val,
                           options,
                           self._get_id(id, name),
                           **attrs)

    def checkbox(self, name, value="1", checked=False, label=None, id=None,
                 **attrs):
        return tags.checkbox(name,
                             value,
                             self.value(name, checked),
                             label,
                             self._get_id(id, name),
                             **attrs)

    def textarea(self, name, content="", id=None, **attrs):
        return tags.textarea(name,
                             self.value(name, content),
                             self._get_id(id, name),
                             **attrs)

    def password(self, name, value=None, id=None, **attrs):
        return tags.password(name, self.value(name, value),
                             self._get_id(id, name),
                             **attrs)

    def is_error(self, name):
        return name in self.errors

    def errors_for(self, name):
        return self.form.errors_for(name)

    def errorlist(self, name):
        errors = self.errors_for(name)

        if not errors:
            return ''

        content = "\n".join(HTML.tag("li", error) for error in errors)
        return HTML.tag("ul", tags.literal(content), class_='error')

    def value(self, name, default=None):
        return self.data.get(name, default)

    def _get_id(self, id, name):
        if id is None:
            id = name
            if self.id_prefix:
                id = self.id_prefix + id
        return id


class FormRenderer(Renderer):
    def __init__(self, form, csrf_field=csrf_field, id_prefix=None):
        self.form = form
        self.csrf_field = csrf_field

        Renderer.__init__(self, form.data, form.errors, id_prefix)

    def begin(self, url=None, **attrs):
        url = url or self.form.request.path
        multipart = attrs.pop('multipart', self.form.multipart)
        return tags.form(url, multipart=multipart, **attrs)

    def end(self):
        return tags.end_form()

    def csrf(self, name=None):
        name = name or self.csrf_field

        token = self.form.request.session.get_csrf_token()
        return self.hidden(name, value=token)

    def csrf_token(self, name=None):
        return HTML.tag('div', self.csrf(name), style='display:none;')
