import ast

from refactor.refactor import (get_class_locals, get_dependencies,
                               get_function_locals, get_module_locals,
                               get_names_used)


def test_get_function_locals():
    source = '\n'.join([
        'def foo(a):',
        '   x = ast.parse("")',
    ])
    tree = ast.parse(source).body[0]
    assert get_function_locals(tree) == {'ast', 'x'}


def test_get_names_used():
    func = [
        'def bar(y):',
        '   x = X()',
        '   foo()',
        '   ast.parse(A)',
    ]
    source = [
        'import ast',
        'from os import path',
        '',
        'A = ""',
        '',
        'def foo():',
        '   return True',
        '',
        'class X(object):',
        '   pass',
        '',
    ] + func
    tree = ast.parse('\n'.join(source))
    node = ast.parse('\n'.join(func)).body[0]
    assert get_names_used(tree, node) == {'A', 'X', 'ast', 'foo'}


def test_get_dependencies():
    tree = ast.parse('\n'.join([
        'import foo',
        'def bar():',
        '   return foo + "x"',
        'def foobar():',
        '   return bar() + foo',
        'x = lambda y: foo',
    ]))
    assert get_dependencies(tree) == {
        'foo': set([]),
        'bar': set(['foo']),
        'foobar': set(['foo', 'bar']),
        'x': set(['foo']),
    }


def test_get_dependencies_class():
    tree = ast.parse('\n'.join([
        'import foo',
        'class Bar(foo):',
        '   pass'
    ]))
    assert get_dependencies(tree) == {
        'foo': set([]),
        'Bar': set(['foo']),
    }


def test_get_class_locals():
    source = [
        'class Bar(object):',
        '   classvar = list()',
        '   def method(self, x, y=1, *args, **kwargs):',
        '       return x + y + z',
    ]
    node = ast.parse('\n'.join(source))
    assert get_class_locals(node) == {'list', 'object', 'z'}


def test_get_module_locals():
    source = [
        'import ast',
        'from os import path',
        'from pprint import pprint as pp',
        'import re as r',
        '',
        'A = ""',
        '',
        'def foo():',
        '   return True',
        '',
        'class X(object):',
        '   pass',
    ]
    node = ast.parse('\n'.join(source))
    assert set(get_module_locals(node)) == {'A', 'X', 'ast', 'foo', 'path',
                                            'pp', 'r'}
