import ast

from refactor import (get_imports, get_function_locals, get_names_used)


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
    tree = ast.parse('\n'.join([
        'import ast',
        'from os import path',
        '',
        'def foo():',
        '   return True',
        '',
        'class X(object):',
        '   pass',
        '',
        'def bar():',
        '   x = X()',
        '   foo()',
        '   ast.parse("")',
    ]))
    source = '\n'.join([
        'def bar():',
        '   x = X()',
        '   foo()',
        '   ast.parse("")',
    ])
    node = ast.parse(source).body[0]
    assert get_names_used(tree, node) == {'X', 'ast', 'foo'}
