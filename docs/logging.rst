Logging
=======

You may wish to maintain a separate log of form validation errors. Built-in support is included using the ``pyramid_uniform.validate`` logging key.

That logger will emit messages like::

    Validation failure on http://example.com/some-url from 1.2.3.4 [Mozilla 5.0]
    Params:
    {'name': 'Something valid', 'integer_value': 'twelve'}
    Errors:
    {'integer_value': 'Must contain an integer'}

Loggers are propagated, so you can use ``pyramid_uniform`` directly.
