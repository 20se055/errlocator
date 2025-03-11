#メッセージ分類後の解析, ルール
import pprint, re, pandas, numpy, os
import opt.sql as sql
import plugin.util_related as ur
import  subprocess, tempfile, shutil
import json
from enum import Enum
import opt.config as cfg

#条件分岐に影響を与える変数を特定
def path(host, user, password, fi, li):   #ファイル名, 行
    with open(fi, 'r') as f:
        lines = f.read().split("\n")
        lines = lines[:li + 1] #linesの要素をliより前のコードだけにする
        lines.reverse()
        for i, x in enumerate(lines):
            if "if" in x:
                idx = li - i#if文行目
                con = x #if文
                break
            else:
                con = None
        lines.reverse()
        
        val = []
        if con == None:
            block, idx = ur.get_block(lines, li)
            idx = idx - 1
            for i in block:
                if re.findall(r'^\s+.+', i):
                    m = re.findall(r'^\s+(.+)', i)
                    i = m[0]
                col = find_col(fi, idx, i)
                if "\n" in i:
                    i = i[:-1]
                sql.insert_formulas(host, user, password, i, fi, idx, col)
                idx = idx + 1
            eq4 = []
        else:
            #条件文だけ抜き出す
            match = re.findall(r'([\w\"\'\(\)\[\],\*\\%\+-:=]+(\s?(==|!=|<=|>=|<|>|not\sin|in|is\snot|is)\s?[\w\"\'\(\)\[\],\*\\%\+-:=]+)?)', con)
            eq = []
            for i in match:
                eq.append(i[0])
            reserved = ["if", "elif", "and", "or", "not"]
            for i, x in enumerate(eq):
                for j in reserved:
                    if x == j:
                        eq[i] = 0
            eq2 = []
            eq3 = []
            for i, x in enumerate(eq):
                if not x == 0:
                    eq2.append(x)
                else:
                    e = " ".join(eq2)
                    eq3.append(e)
                    eq2 = []
            e = " ".join(eq2)
            eq3.append(e)
            eq4 = [i for i in eq3 if i != '']
            for i, x in enumerate(eq4):
                m = re.findall(r'(.+):$', x)
                if m:
                    eq4[i] = m[0]
            for i in eq4:
                if re.findall(r'^\s+.+', i):
                    m = re.findall(r'^\s+(.+)', i)
                    i = m[0]
                col = find_col(fi, idx, i)
                if "\n" in i:
                    i = i[:-1]
                sql.insert_formulas(host, user, password, i, fi, idx, col)

            #条件文から変数を抜き出す
            for i, x in enumerate(eq4):
                if "is" in x or "in" in x:
                    match = re.findall(r'(.+)\s(not\s)*(is|in)(\snot)*\s(.+)', x)
                    for i, x in enumerate(match):
                        if not "'" in x[0] and not '"' in x[0]:
                            find_insert(host, user, password, fi, idx, x[0])
                            val.append([x[0], fi, idx])
                        if not "'" in x[4] and not '"' in x[4]:
                            find_insert(host, user, password, fi, idx, x[4])
                            val.append([x[4], fi, idx])
                elif ":=" in x:
                    match = re.findall(r'\(.+:=\s*(.+)\)\s*(==|!=|<=|>=|<|>)\s*([^:]+)', x)
                    for i, x in enumerate(match):
                        if not "'" in x[0] and not '"' in x[0]:
                            find_insert(host, user, password, fi, idx, x[0])
                            val.append([x[0], fi, idx])
                        if not "'" in x[2] and not '"' in x[2]:
                            find_insert(host, user, password, fi, idx, x[2])
                            val.append([x[2], fi, idx])
                elif "=" in x or "!" in x or ">" in x or "<" in x:
                    match = re.findall(r'(.+)\s?(==|!=|<=|>=|<|>)\s?(.+)', x)  
                    for h in match:
                        for i in h:
                            if re.findall(r'^\s?[+\-/%*]\s?$', i):
                                pass
                            elif re.findall(r'.+\s?[+\-/%*]\s?.+', i):
                                m = re.findall(r'(.+)\s?[+\-/%*]\s?(.+)', i)
                                for n in m:
                                    find_insert(host, user, password, fi, idx, n[0])
                                    val.append([n[0], fi, idx])
                                    find_insert(host, user, password, fi, idx, n[1])
                                    val.append([n[1], fi, idx])
                else:
                    if not "'" in x and not '"' in x:
                        find_insert(host, user, password, fi, idx, x)
                        val.append([x, fi, idx])
    
    for i, j in enumerate(val):
        if re.findall(r'.+\s$', j[0]):
            val[i][0] = j[0][:-1]

    return val

#()内[]内のワードをDBに追加それ以外はそのまま
def find_insert(host, user, password, fi, idx, eq):
    if "(" in eq and ")" in eq:
        m = re.findall(r'\((.+)\)', eq)
        m = re.findall(r'(\w+)', m[0])
        for i in m:
            db_insert(host, user, password, fi, idx, i)
    elif "[" in eq and "]" in eq:
        m = re.findall(r'\[(.+)\]', eq)
        for i in m:
            db_insert(host, user, password, fi, idx, i)
    else:
        if re.findall(r'.+\s$', eq):
            eq_n = eq[:-1]
        db_insert(host, user, password, fi, idx, eq_n)

#基準行を1行ずつの配列化
def lines(st):
    lin = st.splitlines()
    return lin

# ファイルをオープンして，行単位で配列に格納する
def open_file(file):
    lines = []
    # ファイルを開く
    with open(file, encoding="utf-8") as f:
        # for line in f:
        #     lines.append(line)
        # print(line)
        lines = f.read().split("\n")
    for i, line in enumerate(lines):
        lines[i] = line + '\n'
    return lines

#該当ファイルの中でidx行目のwordが何文字目か出力
def find_col(fi, idx, word):
    # 正規表現に用いる記号が入っていると正規表現がバグるので\\を追加
    # .*+?~[]|()^$\
    # if "\\" in word:
    #     new = "\\\\"
    #     word = word.replace('\\', new)
    synbol = [".", "*", "+", "?", "~", "[", "]", "|", "(", ")", "^", "$"]
    for i in synbol:
        escaped = "\\" + i
        if re.findall(r'[^\\]({})'.format(escaped), word):
            #match = re.findall(r'[^\\]({})'.format(escaped), word)
            new = "\\" + i
            word = word.replace(i, new)
        elif re.findall(r'^({})'.format(escaped), word):
            #match = re.findall(r'^({})'.format(escaped), word)
            new = "\\" + i
            word = word.replace(i, new)
    with open(fi) as f:
        lines = f.readlines()
        if re.match(r'^({})$'.format(word), lines[idx]) or re.match(r'^({})\W'.format(word), lines[idx]):
            start = 0
        elif re.search(r'\W({})\W'.format(word), lines[idx]):
            match = re.search(r'\W({})\W'.format(word), lines[idx])
            start = match.start()
        elif re.search(r'({})'.format(word), lines[idx]):
            match = re.search(r'({})'.format(word), lines[idx])
            start = match.start()
        else:
            m = re.findall(r'\s*\w+\\\(', word)
            word = m[0]
            match = re.search(r'({})'.format(word), lines[idx])
            start = match.start()
        return start

#stの変数を全て取り出す
def all_value(st):
    lin = lines(st)
    match = re.findall(r'(\w+(\.|\()?|\"\w+\"|\'\w+\')', lin[1])
    x = []
    for i in match:
        x.append(i[0])
    x = removed(x)
    for n, m in enumerate(x):
        if '.' in m:
            x[n] = 0
        if '(' in m:
            x[n] = 0
    x = [e for e in x if e != 0]        
    return x

#stringから予約語, 演算子, 文字列, 数字だけの要素を取り除く
def removed(string):
    par = string
    keyword = [
        "False", "await", "else", "import", "pass", "None", "break", "except", 
        "in", "raise", "True", "class", "finally", "is", "return", "and", 
        "continue", "for", "lambda", "try", "as", "def", "from", "nonlocal",
        "while", "assert", "del", "global", "not", "with", "async", "elif", 
        "if", "or", "yield"]
    operator = [ '+', "-", "%", "/", "*", "!", "=", ">", "<", "&", "^", "|", ":"]
    string = ["\'", '\"']
    for i, x in enumerate(par):
        for t, y in enumerate(keyword):
            if par[i] == keyword[t]:
                par[i] = 0
        for t, y in enumerate(operator):
            if operator[t] in x:
                par[i] = 0
        for t, y in enumerate(string):
            if string[t] in x:
                par[i] = 0
        if re.compile(r'^\d+$').search(x):
            par[i] = 0
    new_par = [e for e in par if e != 0]
    #pprint.pprint(new_par)
    return new_par

# 何文字目か所得し，変数をvalues，定数をconstantsに追加
def db_insert(host, user, password, fi, li, word):
    # 正規表現に用いる記号が入っていると正規表現がバグるので\\を追加
        # .*+?~[]|()^$\
        if "\\" in word:
            new = "\\\\"
            word = word.replace('\\', new)
        synbol = [".", "*", "+", "?", "~", "[", "]", "|", "(", ")", "^", "$"]
        for i in synbol:
            escaped = "\\" + i
            if type(word) == str:
                word_list = []
                word_list.append(word)
                word = word_list
            #word = list(word)
            for j, k in enumerate(word):
                if re.findall(r'[^\\]({})'.format(escaped), k):
                    #match = re.findall(r'[^\\]({})'.format(escaped), word)
                    new = "\\" + i
                    word[j] = word[j].replace(i, new)
                elif re.findall(r'^({})'.format(escaped), k):
                    #match = re.findall(r'^({})'.format(escaped), word)
                    new = "\\" + i
                    word[j] = word[j].replace(i, new)
                col = find_col(fi, li, k)
                if re.findall(r'^\d+$', k) or "\'" in word or '\"' in k:
                    sql.insert_constants(host, user, password, k, fi, li, col)
                else:
                    sql.insert_values(host, user, password, k, fi, li, col)

# 何文字目か所得し，変数をadd_values，定数をconstantsに追加
def db_insert_re(host, user, password, fi, li, word):
    col = find_col(fi, li, word)
    if re.findall(r'^\d+$', word) or "\'" in word or '\"' in word:
        sql.insert_constants(host, user, password, word, fi, li, col)
    else:
        sql.insert_add_values(host, user, password, word, fi, li, col)

# 何文字目か所得し，formulasに追加
def formula_insert(host, user, password, fi, li, formula):
    col = find_col(fi, li, formula)
    sql.insert_formulas(host, user, password, formula, fi, li, col)

# 出力にハイライトを加える
def print_hl(text, highlight, keyword, color="reverse"):
    color_dic = {'yellow':'\033[43m', 'red':'\033[41m', 'blue':'\033[44m', 'reverse':'\033[07m', 'cyan':'\033[46m', 'end':'\033[0m'}
    for kw in keyword:
        text = text.replace("\n", "")
        synbol = [".", "*", "+", "?", "~", "[", "]", "|", "(", ")", "^", "$"]
        for i in synbol:
            escaped = "\\" + i
            if re.findall(r'[^\\]({})'.format(escaped), kw):
                match = re.findall(r'[^\\]({})'.format(escaped), kw)
                new = '\\' + i
                kw = kw.replace(i, new)
            elif re.findall(r'^({})'.format(escaped), kw):
                match = re.findall(r'^({})'.format(escaped), kw)
                new = '\\' + i
                kw = kw.replace(i, new)
        if re.findall(r'(^|\W)({})(\W|$|\n)'.format(kw), text):
            match = re.findall(r'((^|\W)({})(\W|$|\n))'.format(kw), text)
            bef = match[0][2]
            aft = color_dic[color] + bef + color_dic["end"]
            aft = '\033[1m' + aft + color_dic["end"]
            m = re.findall(r'(^|\W)({})(\W|$)'.format(kw), text)
            aft = m[0][0] + aft + m[0][2]
            r = '(^|\W)({})(\W|$)'.format(kw)
            text = re.sub(r, aft, text)
    print(text)

# 出力・ファイル初期化
def out_reset(formula, li, line, keyword, lines, highlight, fi):
    keyword.sort(key=len, reverse=True)
    line = sorted(line)

    # インデントありのとき
    if not re.findall(r'^[^\s]+', lines[li]):
        print_time = 0
        for i, j in enumerate(line):
            block, block_st, block_en = ur.get_block(lines, j)
            block_st = block_st
            block_en = block_en + 1
            if i == 0:
                print_block_st = block_st
                print_block_en = block_en
            else:
                inc = 0 # 初期値＆完全に別ブロック
                if block_st >= print_block_st and block_en <= print_block_en:
                    inc = 1 # 新しいブロックの方が小さい 
                elif block_st <= print_block_st and block_en >= print_block_en:
                    inc = 2 # 新しいブロックの方が大きい
                    print_block_st = block_st
                    print_block_en = block_en
                if inc == 0:
                    if print_time != 0:
                        print("~~~")
                    print_time = print_time + 1
                    lines_n = lines[print_block_st:print_block_en]
                    #pprint.pprint(lines_n)
                    for l in lines_n:
                        l = str(print_block_st + 1) + ":\t" + l
                        if print_block_st in line:
                            print_hl(l, highlight, keyword)
                        else:
                            print(l, end='')
                        print_block_st = print_block_st + 1
                    print_block_st = block_st
                    print_block_en = block_en
        print("~~~")
        lines_n = lines[print_block_st:print_block_en]
        for l in lines_n:
            l = str(print_block_st + 1) + ":\t" + l
            if print_block_st in line:
                print_hl(l, highlight, keyword)
            else:
                print(l, end='')
            print_block_st = print_block_st + 1
                    

            # if i != 0:
            #     block_n, block_st_n, block_en_n = ur.get_block(lines, line[i - 1])
            #     if block_st >= block_st_n and block_en <= block_en_n:
            #         break
            #     else:
            #         print("~~~")
            #         li_min = block_st
            #         li_max = block_en + 1
            #         lines_n = lines[li_min:li_max]
            #         for l in lines_n:
            #             l = str(li_min + 1) + ":\t" + l
            #             if li_min in line:
            #                 print_hl(l, highlight, keyword)
            #             else:
            #                 print(l, end='')
            #             li_min = li_min + 1
                        
            # else:
            #     li_min = block_st
            #     li_max = block_en + 1
            #     lines_n = lines[li_min:li_max]
            #     for j, k in enumerate(lines_n):
            #         if k[-1] == '\n':
            #             lines_n[j] == k[-1]
            #     for l in lines_n:
            #         l = str(li_min + 1) + ":\t" + l
            #         if li_min in line:
            #             print_hl(l, highlight, keyword)
            #         else:
            #             print(l, end='')
            #         li_min = li_min + 1
    
    # インデントなしのとき
    else:
        print_block_st = line[0]
        print_block_en = line[-1] + 1
        lines_n = lines[print_block_st:print_block_en]
        for l in lines_n:
            l = str(print_block_st + 1) + ":\t" + l
            if print_block_st in line:
                print_hl(l, highlight, keyword)
            else:
                print(l, end='')
            print_block_st = print_block_st + 1

# 出力・構築
def out_build(fi, formula, li):
    line = []
    keyword = []
    print(fi)
    lines = open_file(fi)
    keyword.append(formula)
    line.append(li)
    return keyword, line, lines

def _load_config(name):
    _chk_config(name)
    return None if not hasattr(cfg, name) or getattr(cfg, name) is None else getattr(cfg, name)

def _chk_config(name):
    if not hasattr(cfg, name) or getattr(cfg, name) is None:
        cfg.load_config()

def c_compiler():
    compiler = _load_config('c_compiler')
    return "python3" if compiler is None else compiler

### コンパイル処理．コンパイル結果を，行ごとに配列にして返却．
def compile_process(src, exec, warn, arg, cwd=None, display=False):
    cmd = ["python3"]
    if warn != None:
        cmd.extend(["-W" + warn])
    if exec != None:
        cmd.extend(["-o", exec])
    # if cwd != None:
    #     log.print("== source file " + os.path.join(cwd, src) + " start ==")
    #     log.print("".join(open_file(os.path.join(cwd, src))).rstrip())
    #     log.print("== end of file ==")
    cmd.extend([src])
    cmd_str = ''
    for str in cmd:
        cmd_str += str + ' '
    if arg != None:
        for i in arg:
            cmd.extend([i])
    # log.print("[Executed command] " + cmd_str)
    cp_compile = subprocess.run(cmd, capture_output=True, cwd=cwd)
    errmsg = cp_compile.stderr.decode("utf8")
    # if display:
    #     log.print("[Compile Error Messages]")
    #     log.print(errmsg, end='')
    errmsg = errmsg.rstrip()
    
    print(errmsg)
    return errmsg

def debug_mode():
    return True if _load_config('debug_mode') == "True" else False

def display_err():
    return True if _load_config('display_err') == "True" else False