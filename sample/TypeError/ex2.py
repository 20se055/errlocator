import ast

class TypeChecker(ast.NodeVisitor):
    def visit_Call(self, node):
        for arg in node.args:
            if isinstance(arg, ast.Str):  # 文字列が引数に含まれている場合
                print(f"TypeError: 文字列が引数に含まれています: {arg.s} (line {node.lineno})")
            elif isinstance(arg, ast.Num) and isinstance(arg.n, int):
                pass  # 整数の場合は何もしない
            else:
                print(f"TypeError: 不明な型が引数に含まれています (line {node.lineno})")

def check_for_type_errors(code):
    try:
        tree = ast.parse(code)
        checker = TypeChecker()
        checker.visit(tree)
    except SyntaxError as e:
        print(f"SyntaxError: {e}")

# テスト用のコード
source_code = """
def sum(n):
    s = 0
    for i in range(1, n + 1):
        s += i
    return s

x = "9"
print(sum(x))
"""

check_for_type_errors(source_code)
