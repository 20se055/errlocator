import re, pprint, os
import opt.util as util
import opt.sql as sql
import opt.errormessage as err

# 変数の式を含むブロックを取得
def get_block(lines, li):
    # インデントの数カウント
    cnt = 0
    for i in lines[li]:
        if i == ' ':
            cnt = cnt + 1
        else:
            break
    r = ' ' * cnt
    
    # 変数の式を含むブロックを取得
    block = []
    if cnt == 0:
        block_st = block_en = li - 1
        block.append(lines[li - 1])
        for i in lines[li + 1::]:
            if re.findall(r'^\s.+', i):
                block.append(i)
            elif i == "\n":
                block.append(i)
            else:
                break
            block_en = block_en + 1
    else:
        block_st = block_en = li
        for i in lines[li::-1]:
            if re.findall(r'^({})\s*'.format(r), i):
                block.append(i)
            elif "#" in i or re.findall(r'^\s+$', i):
                block.append(i)
            else:
                block.append(i)
                break
            block_st = block_st - 1
        block.reverse()
        for i in lines[li + 1::]:
            if re.findall(r'^({})\s*.*'.format(r), i):
                block.append(i)
            elif i == "\n" or re.findall(r'^\s+$', i):
                block.append(i)
            else:
                break
            block_en = block_en + 1
    
    # if block[0] == "\n":
    #     del block[0]
    #     block_st = block_st + 1
    # if block[-1] == "\n":
    #     del block[-1]
    #     block_en = block_en - 1
    # if block[-2] == "\n":
    #     del block[-2]
    #     block_en = block_en - 1
    # for b in block[:-1]:
    #     if re.findall(r'^\n$', block[n]):
    #         del block[n]
    #         n = n - 1
    #     else:
    #         del block[n]
    #         break
    for b in block:
        if re.findall(r'^\n$', block[0]):
            del block[0]
            block_st = block_st + 1
        else:
            break
    block.reverse()
    for b in block:
        if re.findall(r'^\n$', block[0]):
            del block[0]
            block_en = block_en - 1
        else:
            break
    block.reverse()        

    if len(block) == 1:
        block_st = block_en = li
        for i in lines[li::-1]:
            if re.findall(r'^\S+', i):
                block.append(i)
            else:
                break
            block_st = block_st - 1
        block.reverse()
        for i in lines[li + 1::]:
            if re.findall(r'^\S+', i):
                block.append(i)
            else:
                break
            block_en = block_en + 1
    
    return block, block_st, block_en

# ブロックに繰り返しがあるか判定
def judge_repeat(block):
    x = 0
    if "for" in block[0] or "while" in block[0]:
        x = 1
    return x

# xより前を対象に代入式を探す
def before_line_assign(lines, x, value):
    ass = None
    if "self." in value:
        value = value[5:]
    for i in lines[x::-1]:
        if not ">>>" in i:
            if "," in i:
                if re.findall(r'^\s*({})(,\s*\w+)+\s*=\s*.+'.format(value), i) or re.findall(r'^\s*\w+(,\s*\w+)*(,\s*({}))(,\s*\w+)*\s*=\s*.+'.format(value), i):
                    ass = i
                    break
                elif re.findall(r'[^\w]({})\s*=\s*.+'.format(value), i) or re.findall(r'^({})\s*=\s*.+'.format(value), i):
                    if re.findall(r'[^\w]({})\s*=\s*[^\(,]+'.format(value), i):
                        match = re.findall(r'[^\w](({})\s*=\s*[^\(,]+)'.format(value), i)
                    elif re.findall(r'[^\w]({})\s*=\s*.+'.format(value), i):
                        match = re.findall(r'[^\w](({})\s*=\s*.+)'.format(value), i)
                    else:
                        match = re.findall(r'^(({})\s*=\s*.+)'.format(value), i)
                    ass = match[0][0]
                    break
            else:
                if re.findall(r'[^\w]({})\s*=\s*.+'.format(value), i) or re.findall(r'^({})\s*=\s*.+'.format(value), i):
                    ass = i
                    break
    
    if not ass == None and re.findall(r'[^\(]+\)', ass):
        ass = i[:-1]
    return ass

# スタックトレース内の別ファイルの探索
def other_file(host, user, password, values, formulas, stacktrace, st, value, func):
    i = stacktrace.index(st)
    i_new = i - 1
    if i_new < 0 and not "\\" in value:
        print(str(value) + ": 代入式が見つかりません")
    else:
        fi, li = err.locate(stacktrace[i_new])
        # ファイルが存在するか(ライブラリでないか)判定
        is_file = os.path.isfile(fi)
        if not is_file and not "\\" in value:
            print(str(value) + ": 代入式が見つかりません")
        elif "\\" in value:
            pass
        else:
            formulas = find_assignment(host, user, password, values, formulas, fi, li, value, stacktrace, stacktrace[i_new], func)               

# 何文字目か所得し，変数をadd_values，定数をconstantsに追加
# def db_insert(host, user, password, fi, li, word):
#     col = util.find_col(fi, li, word)
#     if re.findall(r'\d+', word) or "\'" in word or '\"' in word:
#         sql.insert_constants(host, user, password, word, fi, li, col)
#     else:
#         sql.insert_add_values(host, user, password, word, fi, li, col)

def find_assignment(host, user, password, values, formulas, fi, li, value, stacktrace, st, func):
    # ファイル読み込み
    lines = util.open_file(fi)
    lines_r = lines[:li]
    lines_r.reverse()
    # 変数の式を含むブロックを取得
    block, block_st, block_en = get_block(lines, li)
    # 繰り返しがあるか判定
    x = judge_repeat(block)
    if x == 0:
        # 繰り返しなし
        # liより前を対象に代入式を探す
        ass = before_line_assign(lines, li, value)
    else:
        # 繰り返しあり
        # blockより前を対象に代入式を探す
        ass = before_line_assign(lines, block_en, value)
    if ass == None:
        # 代入式なし
        # 該当の式を含む関数が__init__関数か判定
        magic = None
        for i in lines_r:
            if re.findall(r'^\w+', i):
                break
            elif "def" in i and re.findall(r'__\w+__', i):
                magic = i
                match = re.findall(r'\s*(.+):', magic)
                idx = lines.index(magic)
                formulas.append([fi, idx, match[0]])
                break
            elif "class" in i or "def" in i:
                break
        if magic != None:
            # クラス名取得
            idx = lines.index(magic)
            lines_r = lines[:idx]
            lines_r.reverse()
            for i in lines_r:
                if "class" in i:
                    cl = i
                    idx = lines.index(cl)
                    match = re.findall(r'(class\s.+):', cl)
                    formulas.append([fi, idx, match[0]])
                    break
            # クラスのインスタンス生成を探索
            match = re.findall(r'class\s(.+):', cl)
            cl = match[0]
            for i in lines:
                if re.findall(r'.+\s*=\s*{}'.format(cl), i) and not ">>>" in i:
                    ins = i
                    idx = lines.index(i)
                    match = re.findall(r'\s*(.+)', i)
                    formulas.append([fi, idx, match[0]])
                    break
            # インスタンスをadd_values追加
            match = re.findall(r'\s*(.+)\s*=\s*\w+\(.*\)+', ins)
            if match[0][-1] == " ":
                match[0] = match[0][:-1]
            values.append([fi, idx, match[0]])
        elif re.findall(r'.+\s*=\s*[A-Z]\w+\(.*\)', lines[li]):
            # インスタンス生成の式
            m = re.findall(r'[A-Z]\w+\((.*)\)', lines[li])
            if m[0] != "":
                ma = re.findall(r'([\w=]+)', m[0])
                for i in ma:
                    values.append([fi, li, i])
            elif re.findall(r'(self.{})\s*=\s*.+'.format(m[0]), lines[li]):
                ma = re.findall(r'(self.{})\s*=\s*.+'.format(m[0]), lines[li])
                values.append([fi, li, ma[0]])
            else:
                for i in lines:
                    if re.findall(r'(self.{})\s*=\s*.+'.format(value), i):
                        ma = re.findall(r'(self.{})\s*=\s*.+'.format(value), i)
                        break
        else:
            # その変数を引数として受け取っている関数の呼び出し式を探索
            # 関数名
            x = 0
            if func == []:
                for j in lines_r:
                    if re.findall(r'def\s\w+\(([\w:\s]+,\s*)*({}([\w:\s]+)*)(,\s*[\w:\s]+)*\)([\s\->]+)*(\w+)*:'.format(value), j):
                        x = 1
                        match = re.findall(r'(def\s(\w+)\((([\w:\s]+),\s*)*({}([\w:\s]+)*)(,\s*([\w:\s]+))*\)([\s\->]+)*(\w+)*):'.format(value), j)
                        m = []
                        for i in match[0]:
                            if i != " " and i != "" and not "," in i and not re.findall(r'^[^\w]', i):
                                m.append(i)
                            elif i == " -> ":
                                break
                        arg = []
                        for a in m:
                            if re.findall(r'^(\w+):\s*(\w+)$', a):
                                x = re.findall(r'(\w+):\s*(\w+)', a)
                                arg.append([x[0][0], x[0][1]])
                            else:
                                arg.append([a, None])
                        # 変数が何番目の引数か取得
                        arg = [i for i in arg if i != "self"]
                        # 関数k[1]の第num引数 (※0始まり)
                        for x, y in enumerate(arg):
                            if y[0] == value:
                                num = x - 1
                                break
                        idx = lines.index(j)
                        func.append([match[0][1], num])
                        formulas.append([fi, idx, match[0][0]])

                        # for k in m2:
                        #     # 変数が何番目の引数か取得
                        #     arg = []
                        #     m = re.findall(r'\((\w+)', k[0])
                        #     arg.append(m[0])
                        #     if re.findall(r'\,\s*(\w+)', k[0]):
                        #         m = re.findall(r'\,\s*(\w+)', k[0])
                        #         arg.append(m[0])
                        #     # k[0]をformulasに追加
                        #     arg = [i for i in arg if i != "self"]
                        #     num = arg.index(value)
                        #     func.append([k[1], num])
                        #     # 関数k[1]の第num引数 (※0始まり)
                        #     idx = lines.index(j)
                        #     # col = util.find_col(fi, idx, k[0])
                        #     # sql.insert_formulas(host, user, password, k[0], fi, idx, col)

                # 呼び出し式
                called = []
                for n, j in enumerate(lines):
                    for k in func:
                        if k[0] in j and not "def" in j:
                            if "(" in j and not ")" in j:
                                m = re.findall(r'^\s*(.+)\n', j)
                                ass = m[0]
                                for l in lines[n + 1::]:
                                    match = re.findall(r'^\s*(.+)', l)
                                    if ")" in l:
                                        ass = ass + match[0]
                                        break
                                    else:
                                        ass = ass + match[0] 
                                ass = ass.replace("\n", "")
                                match = re.findall(r'(({})\([\"\'\w=\,\s-]+\))'.format(k[0]), ass)
                                called.append(ass)
                                formulas.append([fi, n, match[0][0]])

                            else:
                            #if re.findall(r'(({})\([\"\'\w\,\s-]+\))'.format(k[0]), j):
                                match = re.findall(r'(({})\([\"\'\w\,\s-]+\))'.format(k[0]), j)
                                called.append(j)
                                # jをformulasに追加
                                idx = lines.index(j)
                                # col = util.find_col(fi, idx, match[0][0])
                                # sql.insert_formulas(host, user, password, match[0][0], fi, idx, col)
                                formulas.append([fi, idx, match[0][0]])

                # 引数
                for j in called:
                    match = re.findall(r'\([\"\'\w+=\,\s-]+\)', j)
                    # 前に取得した変数と同じ番目の引数を取得
                    arg = []
                    if not ',' in match[0]:
                        m = re.findall(r'\(([-\"\'\w]+)(\s*=\s*\w+)*\)', match[0])
                        arg.append(m[0][0])
                    elif re.findall(r'\,\s*(\w+)', match[0]):
                        m = re.findall(r'\(([-\"\'\w]+)(\s*=\s*\w+)*,.+\)', match[0])
                        arg.append(m[0][0])
                        m = re.findall(r'\,\s*(\w+)(\s*=\s*\w+)*', match[0])
                        for k in m:
                            arg.append(k[0])

                    # match[0]をadd_valuesに追加
                    if j in lines:
                        idx = lines.index(j)
                        if num < 0 or num > len(arg) - 1:
                            values.append([fi, idx, arg[num - 1]])
                        else:
                            values.append([fi, idx, arg[num]])
                    else:
                        for k in formulas:
                            if k[2] in j:
                                for l, m in enumerate(lines[k[1] + 1::]):
                                    if arg[num] in m:
                                        idx = k[1] + l + 1
                                        values.append([fi, idx, arg[num]])
                                        break
                    # db_insert(host, user, password, fi, idx, arg[num - 1])

            if x == 0:
                # ファイル内に代入式，関数共に見つからない
                other_file(host, user, password, values, formulas, stacktrace, st, value, func)
            elif called == []:
                # ファイル内に関数は見つかるが代入式が見つからない
                other_file(host, user, password, values, formulas, stacktrace, st, value, func)

    else:
        # 代入式あり
        # assをformulasに追加
        if ass in lines:
            idx = lines.index(ass)
        else:
            for i, j in enumerate(lines):
                if ass in j:
                    idx = i
                    break
        if re.findall(r'^\s+.+', ass):
            m = re.findall(r'^\s+(.+)', ass)
            ass = m[0]
        col = util.find_col(fi, idx, ass)
        if "\n" in ass:
            ass = ass[:-1]
        #sql.insert_formulas(host, user, password, ass, fi, idx, col)
        formulas.append([fi, idx, ass])

        # 代入式に変数を含むか判定
        if "(" in ass and not ")" in ass:
            for i in lines[idx + 1::]:
                match = re.findall(r'^\s*(.+)', i)
                if ")" in i:
                    ass = ass + match[0]
                    break
                else:
                    ass = ass + match[0]
        match = re.findall(r'[\w,\s]+\s*=\s*(.+)', ass)
        if re.findall(r'\w+\(([\w\,\s=]+)\)', match[0]):
            m = re.findall(r'\w+\(([\w\,\s=]+)\)', match[0])
            n = re.findall(r'(\w+)(\s*=\s*\w+)?', m[0])
            for i in n:
                #db_insert(host, user, password, fi, idx, n[0])
                if i[0] in lines[idx]:
                    values.append([fi, idx, i[0]])
                else:
                    for j, k in enumerate(lines[idx::]):
                        if i[0] in k:
                            idx_n = idx + j
                            values.append([fi, idx_n, i[0]])
                            break
        elif re.findall(r'[A-Z]\w+\(.*\)', match[0]):
            m = re.findall(r'[A-Z]\w+\((.*)\)', match[0])
            if m[0] != "":
                ma = re.findall(r'([\w=]+)', m[0])
                for i in ma:
                    values.append([fi, idx, i[0]])
            else:
                for i in lines:
                    if re.findall(r'(self.{})\s*=\s*.+'.format(value), i):
                        ma = re.findall(r'((self.{})\s*=\s*.+)'.format(value), i)
                        idx = lines.index(i)
                        formulas.append([fi, idx, ma[0][0]])
                        values.append([fi, idx, ma[0][1]])
        elif re.findall(r'(\w*)\s*((\+|-|\*|/|%)+\s*(\w+))+', match[0][0]):
            m = re.findall(r'\w+', match[0][0])
            for i in m:
                #db_insert(host, user, password, fi, idx, m[0])
                values.append([fi, idx, m[0]])
        elif "(" in match[0][0] and ")" in match[0][0]:
            if "+" in match[0][0] or "-" in match[0][0] or "*" in match[0][0] or "/" in match[0][0] or "%" in match[0][0]:
                m = re.findall(r'[\w\,\s\(\)]+', match[0][0])
                for i in m:
                    if m[0][0] == " ":
                        m[0] = m[0][1:]
                    #db_insert(host, user, password, fi, idx, m[0])
                    values.append([fi, idx, m[0]])
        elif re.findall(r'^\w+$', match[0]):
            values.append([fi, idx, match[0]])
    # if "self" in value:
    #     if re.findall(r'.+\s*=\s*\w+', ass):
    #         ass = None
    #values, formulasの要素をそれぞれのテーブルに追加
    if not values == []:
        for i in values:
            util.db_insert_re(host, user, password, i[0], i[1], i[2])
    for i in formulas:
        util.formula_insert(host, user, password, i[0], i[1], i[2])
                        
    # add_valuesに要素が格納されている時，再帰的に代入式を探索
    sql.dupli_add_values(host, user, password)
    if sql.exist_add_values(host, user, password) == 1:
        add = sql.db_to_list(host, user, password, 2)
        add_v = []
        for i in add:
            value = re.findall(r"\'value\': \'([\w=\.]+)\'", i)
            file = re.findall(r"([-\w\/\.]+.py)", i)
            line = re.findall(r"\'line\': (\d+)", i)
            if re.findall(r"\'value\': \'([\w=\.]+)\'", i):
                add_v.append([value[0], file[0], int(line[0])])
        for i in add_v:
            sql.delete1_add_values(host, user, password, i[0])
            if not values == []:
                del values[0]
            formulas = find_assignment(host, user, password, values, formulas, i[1], i[2], i[0], stacktrace, st, func)
    # else:
    #     print("finish")
    return formulas

def extract_related_locations(host, user, password, values, formulas, list, stacktrace, st):
    func = []
    for i in list:
        formulas = find_assignment(host, user, password, values, formulas, i['file'], i['line'], i['value'], stacktrace, st, func)
    return formulas

def no_analysis(host, user, password, values, formulas, list, stacktrace, st):
    return values, formulas