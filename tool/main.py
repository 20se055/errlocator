#!/usr/bin/python3
import opt.errormessage as err
import opt.util as util
import opt.sql as sql
import plugin.util_variable as v_util
import plugin.util_related as r_util
import pprint, json, re, itertools, sys
import argparse

class Logger:
    def __init__(self, debug):
        self.__debug = debug

    def print(self, *args, end='\n'):
        if self.__debug:
            print(*args, end=end)
            return

if __name__ == "__main__":
    ### コマンドライン引数の解析
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="\b\bSource file to compile")
    parser.add_argument("-o", metavar='<file>',help="\b\bPlace the output into <file>.")
    parser.add_argument("-DEBUG", help="\b\bDisplay debug messages", action='store_true')
    parser.add_argument("-d", help="\b\bDisplay compile error messages (when -DEBUG is enabled)", action='store_true')
    parser.add_argument("-W", metavar='\bwarn...', help="Warning options for compiler")
    parser.add_argument("-a", nargs='*', help="プロジェクトの実行に必要な引数(配列)")

    args = parser.parse_args()
    src = args.file
    exec = args.o
    warn = args.W
    arg = args.a
    disp = util.display_err()
    disp = True if args.d else util.display_err()

    log = Logger(True if args.DEBUG else util.debug_mode())

# プログラムの実行結果を得る
errmsg = util.compile_process(src, exec, warn, arg, cwd=None, display=False)
f = open('errmsg.txt', 'w')
f.write(errmsg)
f.close()

if errmsg == "":
    print("プログラムは正常に動作しており，エラーは発生していません．")
else:
    print("-------------------------------------------------------------------------")
    print("Cause of error:")

    # DB情報取得(setup.py)
    with open('setup.py', 'r') as f:
        setup = f.read()
        setup_lis = setup.split('\n')
        f.close()
    for i in setup_lis:
        if 'host = ' in i:
            h = re.findall(r'host \= \'(.+)\'$', i)
            host = h[0]
        elif 'user = ' in i:
            u = re.findall(r'user \= \'(.+)\'$', i)
            user = u[0]
        elif 'password = ' in i:
            p = re.findall(r'password \= \'(.+)\'$', i)
            password = p[0]

    # DBが存在するか判定し，ない場合作成
    x = sql.exist_db_judge(host, user, password)
    if x == 0:
        sql.db_setting(host, user, password)

    # 実行時にDB内の情報が邪魔なので全部削除
    n = 0
    while(n <= 3):
        sql.db_delete(host, user, password, n)
        sql.db_reset(host, user, password, n)
        n = n + 1

    #スタックトレース(配列), メッセージ
    #result, message = err.message(path)
    result , message = err.message(errmsg)
    #基準行
    st = err.standard(result, message)
    #基準行のファイル名, 行番号
    fi, li = err.locate(st)
    li = li - 1
    #詳細メッセージ
    det = err.get_detail(message)
    #波線
    w, mnt, wav, lin = err.is_wave(st)
    #print("lin: " + str(lin))
    if lin != None:
        col = util.find_col(fi, li, lin)
        sql.insert_formulas(host, user, password, lin, fi, li, col)

    #raise構文判定
    lines = util.open_file(fi)
    r = err.is_raise(host, user, password, fi, li, st, lines)
    if r == 0:
        #raiseあり
        val = util.path(host, user, password, fi, li)
        #DB内に要素があるか判定
        x = sql.exist_values(host, user, password)
        if x == 1:
            #DB内の全ての要素で重複を排除
            sql.dupli_values(host, user, password)
            # リスト出力
            sql.db_to_file(host, user, password, 0)
            with open('opt/list/var_list.json') as f0:
                output0 = json.load(f0)
            sql.db_to_file(host, user, password, 1)
            values = []
            formulas = []
            r_util.extract_related_locations(host, user, password, values, formulas, output0, result, st)

        else:
            #DB内空っぽ
            #波線のところだけDBに追加
            if lin != None:
                util.insert_formulas(host, user, password, fi, li, mnt)
                if not wav[0] == "":
                    for i in wav:
                        util.insert_formulas(host, user, password, fi, li, i)

    else:
        #波線判定
        if w == 0:
            #波線あり
            #ルール適用
            json_open = open('opt/rule.json', 'r')
            rule_json = json.load(json_open)
            #print(rule_json.keys())
            # コンパイルエラーの各行を，行単位でルールと比較
            for rule in rule_json:
                # 各ルールと，if 部を比較
                if char := re.match(rule_json[rule]["variable"]["if"], message):
                    print("Matched: { rule: " + rule + " }")
                    #, { variable }, { line: " + message.rstrip() + " }")
                    # ソースコードを読込み
                    lines = util.open_file(fi)
                    # values = [[ファイル, 行, 変数または定数], [...], ...]3次元配列
                    values = []
                    formulas = []
                    # then 部に記載されたメソッドに対する呼出し文を生成．
                    cmd = "v_util." + rule_json[rule]["variable"]['then'] + "(values, formulas, message, st, fi, li, mnt, wav, lin)"
                    # print(cmd)
                    # then 部を実施
                    lines_orig = lines
                    values, formulas, fi = eval(cmd)
                    #values, formulasの要素をそれぞれのテーブルに追加
                    for i in values:
                        util.db_insert(host, user, password, i[0], i[1], i[2])
                    for i in formulas:
                        util.formula_insert(host, user, password, i[0], i[1], i[2])
                    #DB内の全ての要素で重複を排除
                    sql.dupli_values(host, user, password)
                    # リスト出力
                    sql.db_to_file(host, user, password, 0)
                    with open('opt/list/var_list.json') as f0:
                        output0 = rule_json[rule]["variable"]['output'][0]
                        output0 = json.load(f0)
                        rule_json[rule]["related"]['params'][0] = output0
                    sql.db_to_file(host, user, password, 1)
                    with open('opt/list/const_list.json') as f1:
                        output1 = rule_json[rule]["variable"]['output'][1]
                        output1 = json.load(f1)
            #DB内に要素があるか判定
            x = sql.exist_values(host, user, password)
            if x == 1:
                for rule in rule_json:
                    # add_values, formulasを初期化
                    sql.db_delete(host, user, password, 2)
                    sql.db_reset(host, user, password, 2)
                    col = util.find_col(fi, li, lin)
                    sql.insert_formulas(host, user, password, lin, fi, li, col)
                    # 各ルールと，if 部を比較
                    if char := type(rule_json[rule]["related"]["params"][0]) == list:
                        # print("Matched: { rule: " + rule + " }, { related }, { line: " + message.rstrip() + " }")
                        # ソースコードを読込み
                        lines = util.open_file(fi)
                        # values = [[ファイル, 行, 変数または定数], [...], ...]3次元配列
                        values = []
                        formulas = []
                        # then 部に記載されたメソッドに対する呼出し文を生成．
                        cmd = "r_util." + rule_json[rule]["related"]['method'] + "(host, user, password, values, formulas, rule_json[rule]['related']['params'][0], result, st)"
                        # print(cmd)
                        # then 部を実施
                        lines_orig = lines
                        formulas = eval(cmd)
                        # #values, formulasの要素をそれぞれのテーブルに追加
                        # for i in values:
                        #     util.db_insert_re(host, user, password, i[0], i[1], i[2])
                        # for i in formulas:
                        #     util.formula_insert(host, user, password, i[0], p[1], i[2])
                        
            else:
                #DB内空っぽ
                #波線のところだけDBに追加
                if not lin == None:
                    util.formula_insert(host, user, password, fi, li, mnt)
                    if not wav[0] == "":
                        for i in wav:
                            util.formula_insert(host, user, password, fi, li, i)

        else:
            #行全体の変数
            match = util.all_value(st)
            for i in match:
                util.db_insert(host, user, password, fi, li, i)
                col = util.find_col(fi, li, i)
                sql.insert_formulas(host, user, password, i, fi, li, col)
            #DB内の全ての要素で重複を排除
            sql.dupli_values(host, user, password)
            # リスト出力
            sql.db_to_file(host, user, password, 0)
            with open('opt/list/var_list.json') as f0:
                output0 = json.load(f0)
            sql.db_to_file(host, user, password, 1)
            r_util.extract_related_locations(output0, result, st)
    sql.dupli_values(host, user, password)
    sql.dupli_formulas(host, user, password)

    # 出力
    lis = sql.db_to_list(host, user, password, 3)
    highlight = []

    for i in lis:
        formula = re.findall(r"\\?\'formula\\?\': [\"\'](.+)[\"\']\,\s\\?\'file", i)
        file = re.findall(r"\\?\'file\\?\': \'([\w\-\/\.]+)\'", i)
        line = re.findall(r"\\?\'line\\?\': (\d+)", i)
        column = re.findall(r"\\?\'column\\?\': (\d+)", i)
        highlight.append([formula[0], file[0], int(line[0]), int(column[0])])
    highlight = sorted(highlight, key=lambda x: x[1])
    keyword = []
    for i, j in enumerate(highlight):
        # 初めてのファイル
        if i == 0:
            keyword, line, lines = util.out_build(j[1], j[0], j[2])
        elif j[1] != highlight[i - 1][1]:
            keyword.append(formula[0])
            line.append(li)
            util.out_reset(j[0], j[2], line, keyword, lines, highlight, j[1])
            keyword, line, lines = util.out_build(j[1], j[0], j[2])
        # 引き続き
        else:
            keyword.append(j[0])
            line.append(j[2])
    util.out_reset(highlight[-1][0], highlight[-1][2], line, keyword, lines, highlight, highlight[-1][1])

# print("-------------------------------------------------------------------------")
# print("var_list")
# sql.show(host, user, password, 0)
# print("const_list")
# sql.show(host, user, password, 1)
# print("add_values(正常に動作していれば絶対に空)")
# sql.show(host, user, password, 2)
# print("formulas")
# sql.show(host, user, password, 3)