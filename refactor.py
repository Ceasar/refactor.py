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


class ModuleLocalsVisitor(ast.NodeVisitor):
    """Fetches all the names in an AST."""
    def __init__(self):
        self.locals_ = set()

    def visit_ClassDef(self, node):
        self.locals_.add(node.name)

    def visit_FunctionDef(self, node):
        self.locals_.add(node.name)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.locals_.add(alias.name)

    def visit_Import(self, node):
        for alias in node.names:
            self.locals_.add(alias.name)

    def visit_Name(self, node):
        self.locals_.add(node.id)


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
    module_locals = get_module_locals(tree)
    function_locals = get_function_locals(node)
    return module_locals & function_locals
