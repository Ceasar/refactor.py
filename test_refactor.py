import ast

from refactor import (get_imports, get_imports_used, get_names)


def test_get_imports():
    source = '\n'.join([
        'import ast',
        'from os import path',
    ])
    tree = ast.parse(source)
    assert len(get_imports(tree)) == 2


def test_get_imports_used():
    imports = get_imports('\n'.join([
        'import ast',
        'from os import path',
    ]))
    source = '\n'.join([
        'def foo():',
        '   ast.parse("")',
    ])
    tree = ast.parse(source).body[0]
    assert get_imports_used(tree, imports) == {'ast'}


def test_get_names():
    source = '\n'.join([
        'def foo():',
        '   x = ast.parse("")',
    ])
    tree = ast.parse(source).body[0]
    assert get_names(tree) == {'ast', 'x'}
