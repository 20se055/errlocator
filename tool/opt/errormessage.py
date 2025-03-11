#エラーメッセージ解析処理部
import pprint, re, os
import opt.util as util
import opt.sql as sql
    
#エラーメッセージをスタックトレース、メッセージに分類配列化
def message(errmsg):    
    lines = errmsg.splitlines()

    #エラーメッセージ最下行をメッセージとする
    message = lines[-1]

    #スタックトレースを各行を要素として配列化
    stacktrace = lines
    if 'Traceback' in stacktrace[0]:
        del stacktrace[0]
    del stacktrace[-1]
    lst = []
    result = []
    for i, x in enumerate(stacktrace):  #iがインデックス番号
        x = x[2:] 
        x += '\n'
        if 'File' in x:
            result.append(''.join(lst))
            lst = []
            lst.append(x)
        else:
            lst.append(x) 
    result.append(''.join(lst))   
    del result[0]

    return result, message

#基準行を見つける
def standard(result, message):
    rev = reversed(result)
    st = None
    for i, x in enumerate(rev):
        file = re.findall(r'File\s\"([/\-\w.]+\.py)\"', x)
        if "^" or "~" in x:
            # PC内にファイルが存在するか判定
            is_file = os.path.isfile(file[0])
            if is_file:
                st = result[len(result) - 1 - i]
                break
    if st == None:
        print(result)
        st = result[-1]
            
    return st   #基準行

#基準行からファイル名、行番号を出力
def locate(st):
    #"py", "line"というワードを元に取りだす
    fi = re.findall('/.+py', st)
    fi = fi[0]

    li = re.findall('line.[0-9]+', st)
    li = re.findall('[0-9]+', str(li))
    li = li[0]
    li = int(li)

    return fi, li

#messageから詳細メッセージ取得
def get_detail(message):
    if re.findall(r'.*Error:\s(.*)', message):
        det = re.findall(r'.*Error:\s(.*)', message)
        det = det[0]
    else:
        det = message

    return det

#^^^が引かれているところを出力
def mount(st):
    lin = util.lines(st)
    num = []
    for i, x in enumerate(lin[2]):
        if '^' in x:
            num.append(i)
    mnt = lin[1][num[0]:num[-1] + 1]

    return mnt

#~~~が引かれているところを出力
def wave(st):
    lin = util.lines(st)
    wav = []
    for i, x in enumerate(lin[2]):
        if '~' in x:
            wav.append(lin[1][i])
    wav = ''.join(wav)
    wav_list = []
    wav_list = (wav.split('  '))

    return wav_list

#~~~^^^~~~が引かれているところを出力
def line(st):
    lin = util.lines(st)
    num = []
    for i, x in enumerate(lin[2]):
        if not ' ' in x:
            num.append(i)
    mnt = lin[1][num[0]:num[-1] + 1]

    return mnt

#raise構文かどうか判定
def is_raise(host, user, password, fi, li, st, lines):
    if 'raise' in st:
        r = 0
        st_l = st.splitlines()
        for i in st_l:
            if re.findall(r'raise\s.+', i):
                match = re.findall(r'raise\s.+', i)
                for j, k in enumerate(lines):
                    if i in k:
                        idx = j
                # idx = lines.index(i)
                col = util.find_col(fi, idx, match[0])
                sql.insert_formulas(host, user, password, match[0], fi, idx, col)
    else:
        r = 1
    
    return r

#波線があるか判定
def is_wave(st):
    s = util.lines(st)

    if '^' in s[-1] or '~' in s[-1]:
        n = 0
        mnt = mount(st)
        wav = wave(st)
        lin = line(st)
    else:
        n = 1
        mnt = wav = lin = None

    return n, mnt, wav, lin