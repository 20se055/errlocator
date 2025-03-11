# 氏名自動生成器
import numpy as np
import pandas as pd
import name_gen as nm

# ファイルのURL
u = "https://python.atelierkobato.com/wp-content/uploads/2019/08/name_s.csv"

# ファイルをデータフレームとして読み込む
data = pd.read_csv(u,  encoding="SHIFT-JIS")

# name_sample.csv をフォルダに保存
data.to_csv("name_list")

# フォルダからデータを読み込んで変数 data を上書き
# 左端の列を行ラベルとして設定
data = pd.read_csv("name_list", index_col=0)

np.random.seed(0)

data = "data"

for i in range(5):
    name = nm.name_generator(data)
    print(name)

# https://python.atelierkobato.com/name_generator/