Quick Start
===========


Install
-------

Install with pip::

    $ pip install pyramid_uniform


Use in a Pyramid App
--------------------

No ``config.include()`` directive or setting modifications are required to use ``pyramid_uniform``. Instead, two primary classes are used directly: ``Form`` and ``FormRenderer``.

You can use ``Form`` alone to validate and process a form, with a FormEncode Schema.::

    from formencode import Schema, validators
    from pyramid_uniform import Form


    class MySchema(Schema):
        name = validators.String()
        size = validators.Int()
        published = validators.Bool()


    def myview(request):
        obj = ...

        # Initialize the form
        form = Form(request, MySchema)

        # Check for schema validity.
        if form.validate():

           # Update the attributes of obj based on validated form fields.
           form.bind(obj)

A common pattern is to use the same view (or handler action) to show a form and process the result. To do this, use a ``FormRenderer`` class to wrap the ``Form`` instance for presentation.::

    from formencode import Schema
    from pyramid_uniform import Form, FormRenderer


    class MySchema(Schema):
        name = validators.String()
        size = validators.Int()
        published = validators.Bool()


    def myview(request):
        obj = get_thing(request)

        # Initialize the form
        form = Form(request, MySchema)

        # Check for schema validity.
        if form.validate():

            # Update the attributes of obj based on validated form fields.
            form.bind(obj)
            return HTTPFound(...)

        # Form data is not present or not valid, so show the form.
        renderer = FormRenderer(form)
        return {'renderer': renderer, 'obj': obj}

To use ``renderer`` in a template, call methods on it to generate HTML form tags::

    <h1>Edit ${obj}</h1>

    ${renderer.begin()}
      ${renderer.text('name', obj.name)}
      ${renderer.select('size', obj.size, range(10))}
      ${renderer.checkbox('published', checked=obj.published)}
    ${renderer.end()}

Extensive customization of the validation and rendering behavior is possible. For details, see the API documentation.
