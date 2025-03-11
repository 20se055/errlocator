import numpy as np

def name_generator(data):
    
    # 苗字(surname)の個数
    ct_s = data["苗字"].count()
    
    # 男性(male)の名前の個数
    ct_m = data["名前(男)"].count()

    # 女性(female)の名前の個数
    ct_f = data["名前(女)"].count()
    
    # 性別をランダムに選択
    sex = np.random.choice(["f", "m"])
    
    # 乱数を生成("苗字"の行番号)
    rd_s = np.random.randint(0, ct_s)
    
    if sex == "m":
        k = 2
        sex_label = "男"
        rd_n = np.random.randint(0, ct_m)
    else:
        k = 4
        sex_label = "女"
        rd_n = np.random.randint(0, ct_f)

    # データフレームの配列にアクセス
    dv = data.values

    # 氏名とふりがなを作成
    name = dv[rd_s, 0] + " " + dv[rd_n, k]
    ph = dv[rd_s, 1] + " " + dv[rd_n, k + 1]

    # 関数の戻り値
    return (name, ph, sex_label)