def find_type_mismatch(code):
    # ソースコードの中で関数呼び出し部分を検索します
    for line_num, line in enumerate(code.split('\n')):
        if "sum(" in line:
            # 関数呼び出し部分を分割して引数部分を取得します
            start_index = line.index("sum(") + len("sum(")
            end_index = line.index(")", start_index)
            arguments = line[start_index:end_index].strip()

            # 引数が文字列かどうかをチェックします
            if arguments.isdigit():
                print(f"Line {line_num + 1}: {arguments} は整数です")
            else:
                print(f"Line {line_num + 1}: {arguments} は整数ではありません")

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

find_type_mismatch(source_code)
