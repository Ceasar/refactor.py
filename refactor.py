import ast


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


def get_imported_names(tree):
    visitor = ImportVisitor()
    visitor.visit(tree)
    return {node.name for import_ in visitor.imports for node in import_.names}


class NameVisitor(ast.NodeVisitor):
    """Fetches all the names in an AST."""
    def __init__(self):
        self.names = set()

    def visit_Name(self, node):
        self.names.add(node.id)


def get_names(tree):
    visitor = NameVisitor()
    visitor.visit(tree)
    return visitor.names


def get_imports_used(tree, imports):
    return get_names(tree) & imports
