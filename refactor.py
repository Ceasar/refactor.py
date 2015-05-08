import ast
import sys

import astor


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
    visitor = FunctionLocalsVisitor()
    visitor.visit(tree)
    return visitor.locals_


def get_names_used(tree, node):
    """Get all names in *tree* used by *node*."""
    module_locals = set(get_module_locals(tree))
    function_locals = get_function_locals(node)
    return module_locals & function_locals


def move_node(tree, node, new_tree, module_name):
    """
    Move *node* in *tree* and all of its dependences to *new_tree*.
    """
    names_used = get_names_used(tree, node)
    module_locals = get_module_locals(tree)
    # if it's an import, import it, otherwise import it from this module
    to_import = set()
    for name in names_used:
        dependency_node = module_locals[name]
        if type(dependency_node) in (ast.Import, ast.ImportFrom):
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


def main(name):
    with open('refactor.py') as fp:
        tree = ast.parse(fp.read())
    nodes = get_module_locals(tree)
    new_tree = move_node(tree, nodes[name], ast.parse(''), 'refactor.py')
    return to_source(new_tree)


def to_source(node):
    return astor.codegen.to_source(node)

if __name__ == '__main__':
    print main(sys.argv[1])
