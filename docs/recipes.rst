Recipes
=======

Validating Non-User Input
-------------------------

It's often important to validate input that is not entered directly by a user,
but is still untrusted. For example, a client process running on a remote
machine may construct a URL algorithmically.

In this case, we don't want to deal with the full 'plumbing' of form error
rendering, we just want to make sure the input is safe.
:py:meth:`pyramid_uniform.Form.assert_valid` can be used for this purpose.

.. code-block:: python

    from pyramid_uniform import Form

    Form(request, MySchema).assert_valid()


Skipping CSRF Protection
------------------------

CSRF protection is always on by default. To skip it, pass ``skip_csrf=True`` to
any relevant methods.

.. code-block:: python

    form = Form(request, MySchema)
    if form.validate(skip_csrf=True):
         pass
