import re
import opt.util as util
import opt.sql as sql

# ファイルをオープンして，行単位で配列に格納する
def open_file(file):
    lines = []
    # ファイルを開く
    with open(file, encoding="utf-8") as f:
        for line in f:
            lines.append(line)
    return lines

def extract_left_token(values, formulas, message, st, fi, li, mnt, wav, lin):
    # 1つ目の~~部(wav[0])の変数を抽出
    if "+" in wav[0]:
        match = re.findall(r'.+\+\s?(.+)$', wav[0])
        #util.db_insert(fi, li, match[0])
        values.append([fi, li, match[0]])
    else:
        #util.db_insert(fi, li, wav[0])
        values.append([fi, li, wav[0]])

    return values, formulas, fi

def extract_plus_token(values, formulas, message, st, fi, li, mnt, wav, lin):
    # ~~部の変数を抽出
    formulas.append([fi, li, lin])
    tokens = re.findall(r'(\w+)\s?\+\s?(\w+)', lin)
    for i in tokens:
        values.append([fi, li, i])
        print(i)

    return values, formulas, fi

def extract_mnt_func_token(values, formulas, message, st, fi, li, mnt, wav, lin):
    # ^^部があるか判定
    # ┗ あり：^^部の（）内の変数を特定
    # 　なし：stの下から2行目の()内の変数を特定
    if not mnt == None:
        word = re.findall(r'\((.+)\)', mnt)
        word = str(word[0])
    else:
        l = util.lines(st)
        word = re.findall(r'\((.+)\)', l[1])
    #util.db_insert(fi, li, word)
    values.append([fi, li, word])

    return values, formulas, fi

def optional_argument(values, formulas, message, st, fi, li, mnt, wav, lin):
    # ～番目の引数
    num = re.findall(r'\s(\d+)\s', values, message)
    num = int(num[0]) - 1

    arg = re.findall(r'\((.+)\)', mnt)
    arg = re.findall(r'\s?([^,\(\)]+)', arg[0])

    #util.db_insert(fi, li, arg[num])
    values.append([fi, li, arg[num]])

    return values, formulas, fi

def all_argument(values, formulas, message, st, fi, li, mnt, wav, lin):
    #全ての引数
    arg = re.findall(r'\s*([^,])', mnt)

    for i in arg:
        #util.db_insert(fi, li, i)
        values.append([fi, li, i])

    return values, formulas, fi

def strip_list_key(values, formulas, message, st, fi, li, mnt, wav, lin):
    # ^^部から[ ]を削除
    mnt = mnt.strip("[]")
    #util.db_insert(fi, li, mnt)
    values.append([fi, li, mnt])

    return values, formulas, fi

def extract_mnt_token(values, formulas, message, st, fi, li, mnt, wav, lin):
    # util.db_insert(fi, li, mnt)
    # col = util.find_col(fi, li, mnt)
    # sql.insert_formulas(mnt, fi, li, col)
    formulas.append([fi, li, mnt])

    return values, formulas, fi

def find_arg(values, formulas, message, st, fi, li, mnt, wav, lin):
    arg = re.findall(r'\((.+)\)', mnt)
    arg = re.findall(r'\s?([^,\(\)]+)', arg[0])
    
    for i in arg:
        #util.db_insert(fi, li, i)
        values.append([fi, li, i])

    return values, formulas, fi

# def extract_dic_key(values, formulas, message, st, fi, li, mnt, wav, lin):
#     mnt = mnt.strip("[]")
#     #util.db_insert(fi, li, mnt)
#     values.append([fi, li, mnt])

#     return values, formulas, fi

def extract_dic_name_key(values, formulas, message, st, fi, li, mnt, wav, lin):
    # 辞書名抽出(~~部)
    # 辞書名col特定
    # ^^部([キー])[ ]を削除
    # 　キー名のcolを特定
    dic = wav[0]
    # col = util.find_col(fi, li, wav[0])
    # sql.insert_values(dic, fi, li, col)
    values.append([fi, li, wav[0]])

    mnt = mnt.strip("[]")
    #util.db_insert(fi, li, mnt)
    values.append([fi, li, mnt])

    return values, formulas, fi

def extraxt_mnt_previous_token(values, formulas, message, st, fi, li, mnt, wav, lin):
    # ^^部とひとつ前の単語を抽出
    #util.db_insert(fi, li, mnt)
    values.append([fi, li, mnt])

    lin = util.lines(st)
    match = re.findall(r'([^\s]+)\s' + mnt + r'\s', lin[1])
    if match:
        #util.db_insert(fi, li, match[0])
        # col = util.find_col(fi, li, match[0])
        # sql.insert_formulas(match[0], fi, li, col)
        formulas.append([fi, li, match[0]])

    return values, formulas, fi

# 文字列名とインデックスを取得
def extract_string_indices(values, formulas, message, st, fi, li, mnt, wav, lin):
    #util.db_insert(fi, li, wav[0])
    values.append([fi, li, wav[0]])
    if "[" in mnt and "]" in mnt:
        mnt = mnt.replace("[", "")
        mnt = mnt.replace("]", "")
    #util.db_insert(fi, li, mnt)
    values.append([fi, li, mnt])

    # col = util.find_col(fi, li, lin)
    # sql.insert_formulas(lin, fi, li, col)
    formulas.append([fi, li, lin])

    return values, formulas, fi

# 関数の対象となるオブジェクトを抜き出す
def extract_object(values, formulas, message, st, fi, li, mnt, wav, lin):
    # col = util.find_col(fi, li, lin)
    # sql.insert_formulas(lin, fi, li, col)
    formulas.append([fi, li, lin])

    obj = []
    for i in lin:
        if i != ".":
            obj.append(i)
            break
    obj = ''.join(obj)
    #util.db_insert(fi, li, obj)
    values.append([fi, li, obj])

    return values, formulas, fi

# ファイル名を抜き出す
def extract_file(values, formulas, message, st, fi, li, mnt, wav, lin):
    # col = util.find_col(fi, li, mnt)
    # sql.insert_formulas(mnt, fi, li, col)
    formulas.append([fi, li, mnt])

    file = re.findall(r'[^/]+\.py$', fi)
    file = file[0]
    file = '\033[07m' + file + '\033[0m'
    file = '\033[1m' + file + '\033[0m'

    path = re.findall(r'^/[/\w]+/', fi)

    fi = path[0] + file

    return values, formulas, fi

# 計算式や関数呼び出しから変数を抜き出す
def extract_values(values, formulas, message, st, fi, li, mnt, wav, lin):
    # ^^部を演算子で分割
    val = re.findall(r'\s?([.\w\d\(\)\s,]+)\s?', lin)
    for i, j in enumerate(val):
        if j[-1] == r' ':
            val[i] = j[:-1]
    for i in val:
        if '.' in i and '(' in i:
            m = re.findall(r'(\w+)\..+', i)
            #util.db_insert(fi, li, m[0])
            values.append([fi, li, m[0]])
            if ',' in i:
                m0 = re.findall(r'\w+.\w+\((\w+).+\)', i)
                #util.db_insert(fi, li, m0[0])
                values.append([fi, li, m0[0]])
                m0 = []
                m0 = re.findall(r',\s*(\w+)', i)
                for j in m0:
                    for k in j:
                        #util.db_insert(fi, li, k)
                        values.append([fi, li, k])
            else:
                m1 = re.findall(r'\w+.\w+\((\w+)\)', i)
                for j in m1:
                    for k in j:
                        #util.db_insert(fi, li, k)
                        values.append([fi, li, k])
        elif '(' in i:
            if ',' in i:
                m2 = re.findall(r'\w+\((\w+).+\)', i)
                #util.db_insert(fi, li, m2[0])
                values.append([fi, li, m2[0]])
                m2 = []
                m2 = re.findall(r',\s*(\w+)', i)
                for j in m2:
                    for k in j:
                        #util.db_insert(fi, li, k)
                        values.append([fi, li, k])
            else:
                m3 = re.findall(r'\w+\((\w+)\)', i)
                for j in m3:
                    #util.db_insert(fi, li, j)
                    values.append([fi, li, j])
        else:
            #util.db_insert(fi, li, i)
            values.append([fi, li, i])
    
    return values, formulas, fi