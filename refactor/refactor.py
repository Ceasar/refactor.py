"""
Implement several functions for manipulating ASTs of modules.
"""
import ast

import astor

NODES_IMPORT = ast.Import, ast.ImportFrom


class ImportVisitor(ast.NodeVisitor):
    """Fetches all the import statements in an AST."""
    def __init__(self):
        self.imports = []

    def visit_ImportFrom(self, node):
        self.imports.append(node)

    def visit_Import(self, node):
        self.imports.append(node)


def get_imports(tree):
    visitor = ImportVisitor()
    visitor.visit(tree)
    return visitor.imports


class ModuleLocalsVisitor(ast.NodeVisitor):
    """Fetches all the names in an AST."""
    def __init__(self):
        self.locals_ = {}

    def visit_ClassDef(self, node):
        self.locals_[node.name] = node

    def visit_FunctionDef(self, node):
        self.locals_[node.name] = node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.locals_[alias.name] = node

    def visit_Import(self, node):
        for alias in node.names:
            self.locals_[alias.name] = node

    def visit_Name(self, node):
        # Avoid adding uses of a name
        if node.id not in self.locals_:
            self.locals_[node.id] = node


class FunctionLocalsVisitor(ast.NodeVisitor):
    """Fetches all the names in an AST."""
    def __init__(self):
        self.locals_ = set()

    def visit_Name(self, node):
        self.locals_.add(node.id)


def get_module_locals(tree):
    visitor = ModuleLocalsVisitor()
    visitor.visit(tree)
    return visitor.locals_


def get_function_locals(tree):
    """
    Get all the names used by the function at *tree*.

    >>> sorted(get_function_locals(ast.parse('\\n'.join([
    ... 'def foo():',
    ... '   x = list()',
    ... ]))))
    ['list', 'x']
    """
    visitor = FunctionLocalsVisitor()
    visitor.visit(tree)
    return visitor.locals_


class ClassLocalsVisitor(ast.NodeVisitor):
    """Fetches all the names in an AST."""
    def __init__(self):
        self.locals_ = set()
        self.scope_stack = []

    def visit_Assign(self, node):
        if self.scope_stack:
            self.generic_visit(node)
        else:
            # *node* is class variable. Only visit the right hand side.
            self.generic_visit(node.value)

    def visit_FunctionDef(self, node):
        locals_ = self.locals_.copy()
        self.scope_stack.append(node)
        self.generic_visit(node)
        assert self.scope_stack.pop() == node
        scoped_names = {name.id for name in node.args.args}
        if node.args.vararg:
            scoped_names.add(node.args.vararg)
        if node.args.kwarg:
            scoped_names.add(node.args.kwarg)
        new_names = self.locals_ - locals_
        self.locals_ -= new_names & scoped_names

    def visit_Name(self, node):
        self.locals_.add(node.id)


def get_class_locals(node):
    """
    Get all the names used by the function at *tree*.

    >>> sorted(get_function_locals(ast.parse('\\n'.join([
    ... 'class Bar(object):',
    ... '   classvar = list()',
    ... '   def method(self, x, y=1, *args, **kwargs):',
    ... '       return x + y + z',
    ... ]))))
    ['list', 'object', 'z']
    """
    visitor = ClassLocalsVisitor()
    visitor.visit(node)
    return visitor.locals_


def get_names_used(tree, node):
    """Get all names in *tree* used by *node*."""
    module_locals = set(get_module_locals(tree))
    function_locals = get_function_locals(node)
    return module_locals & function_locals


def branch(tree, node, module_name):
    """
    Move *node* in *tree* and all of its dependences to *new_tree*.
    """
    new_tree = ast.parse('')
    names_used = get_names_used(tree, node)
    module_locals = get_module_locals(tree)
    # if it's an import, import it, otherwise import it from this module
    to_import = set()
    for name in names_used:
        dependency_node = module_locals[name]
        if type(dependency_node) in NODES_IMPORT:
            new_tree.body.append(module_locals[name])
        else:
            to_import.add(name)
    new_tree.body.append(ast.ImportFrom(
        module_name,
        [ast.alias(name, None) for name in sorted(to_import)],
        0
    ))
    new_tree.body.append(node)
    return new_tree


def move_node(fp, name):
    tree = ast.parse(fp.read())
    nodes = get_module_locals(tree)
    try:
        node = nodes[name]
    except KeyError:
        raise ValueError('{} not in {}'.format(name, nodes.keys()))
    return to_source(branch(tree, node, fp.name))


def to_source(node):
    return astor.codegen.to_source(node)


def get_dependencies(tree):
    """
    Get a dictionary representing the dependencies between definitions in a
    module.

    >>> tree = ast.parse('\\n'.join([
    ...     'import foo',
    ...     'def bar():',
    ...     '   return foo + "x"',
    ...     'def foobar():',
    ...     '   return bar() + foo',
    ... ]))
    >>> get_dependencies(tree) == {
    ...     'foo': set([]),
    ...     'bar': set(['foo']),
    ...     'foobar': set(['foo', 'bar']),
    ... }
    True
    """
    deps = {}
    module_locals = get_module_locals(tree)
    for name, node in module_locals.items():
        if type(node) in NODES_IMPORT:
            deps[name] = set()
        elif type(node) == ast.ClassDef:
            deps[name] = set(module_locals) & get_class_locals(node)
        elif type(node) == ast.FunctionDef:
            deps[name] = set(module_locals) & get_function_locals(node)
        else:
            raise ValueError("Can't get dependencies for {}".format(name))
    return deps
