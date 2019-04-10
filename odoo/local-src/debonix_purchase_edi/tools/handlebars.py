#! -*- coding: utf-8 -*-
"""
pystache meets handlebars

>>> import string
>>> import handlebars

>>> renderer = handlebars.Renderer()
>>> renderer.register_helper('ljust', string.ljust)
>>> renderer.render("{{ljust income 7 '0'}}", {'income':'30000'})
u'3000000'
>>> renderer.render("{{ljust '' 7 '0'}}", {})
u'0000000'
>>> renderer.render("{{ljust 'abc' 7}}", {})
u'abc    '
>>> renderer.render("{{plain}}", {'plain': 'Hello'})
u'Hello'
"""

import pystache.renderengine
import pystache.renderer
import pystache
import decimal

class Handlebars(object):
    def __init__(self):
        self._renderer = None
        self._original = None

    def __repr__(self):
        return '<Handlebars>'

    def __call__(self, renderer):
        self._renderer = renderer
        return self

    def _context_get(self, stack, name):
        """ FIXME: doc """

        def unquote(arg):
            """ unquote argument """
            if arg == "''":
                return ''
            if arg[0] == "'" and arg[-1] == "'":
                return arg[1:-1]
            return arg

        def casting(arg):
            """ unquote and cast to str """
            return str(unquote(arg))

        def cast(arg):
            """ cast arguments passed to helper function """
            for castor in (int, decimal.Decimal, casting):
                try:
                    return castor(arg)
                except (ValueError, decimal.InvalidOperation,
                        UnicodeEncodeError):
                    pass
            return arg

        if ' ' in name:

            args = name.split()
            fun, name, args = args[0], args[1], [cast(a) for a in args[2:]]
            fun = self._renderer.get_helper(fun)
            val = unquote(name)
            if val == name:
                val = self._original(stack, name)
            val = fun(*[val]+args)
            return val

        val = self._original(stack, name)
        return val

    def __enter__(self):
        """ patch pystache engine to support handlebars style helpers """
        self._original = pystache.renderer.context_get
        pystache.renderer.context_get = self._context_get

    def __exit__(self, exc_type, exc_value, taceback):
        """ unpatch pystache engine after doing the job """
        pystache.renderer.context_get = self._original


class Renderer(pystache.Renderer):
    """ pystache renderer augmented with handlebars style helpers """
    _helpers = {}
    _handlebars = None


    def __init__(self, file_encoding=None, string_encoding=None,
                 decode_errors=None, search_dirs=None, file_extension=None,
                 escape=None, partials=None, missing_tags=None):

        handlebars = Handlebars()
        with handlebars:
            super(Renderer, self).__init__(file_encoding, string_encoding,
                                           decode_errors, search_dirs, file_extension,
                                           escape, partials, missing_tags)
            self._handlebars = handlebars



    def register_helper(self, name, function):
        """ register a helper function for this renderer """
        self._helpers[name] = function

    def get_helper(self, fun):
        """ get registered helper 'fun' """
        return self._helpers[fun]

    def render(self, template, *context, **kwargs):
        with self._handlebars(self):
            return super(Renderer, self).render(template, *context, **kwargs)
