import ast

from refactor.refactor import (get_class_locals, get_dependencies, get_imports,
                               get_function_locals, get_names_used)


def test_get_imports():
    source = '\n'.join([
        'import ast',
        'from os import path',
    ])
    tree = ast.parse(source)
    assert len(get_imports(tree)) == 2


def test_get_function_locals():
    source = '\n'.join([
        'def foo():',
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
    ]))
    assert get_dependencies(tree) == {
        'foo': set([]),
        'bar': set(['foo']),
        'foobar': set(['foo', 'bar']),
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
