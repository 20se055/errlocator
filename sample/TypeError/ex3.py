import ast

class TypeChecker(ast.NodeVisitor):
    def __init__(self):
        self.current_function = None

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)

    def visit_Call(self, node):
        func_name = None
        for child_node in node.args:
            if isinstance(child_node, ast.Str):
                print(f"関数 {self.current_function} の引数が文字列です: {child_node.s}")
            elif isinstance(child_node, ast.Name):
                print(f"関数 {self.current_function} の引数が変数です: {child_node.id}")

def check_for_type_errors(code):
    try:
        tree = ast.parse(code)
        checker = TypeChecker()
        checker.visit(tree)
    except SyntaxError as e:
        print(f"SyntaxError: {e}")

# テスト用のコード
source_code = """
def example_function(arg1, arg2):
    print(arg1 + arg2)

var1 = "20"
example_function(10, var1)
example_function("30", 40)
example_function(50, 60)
"""

check_for_type_errors(source_code)
