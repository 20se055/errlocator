# coding: utf-8
import panda

df = pandas.read_csv('test.csv')
print(df)
print("-"*30)

# 行列に行列を追加 (新しいDataFrame インスタンスが生成される)
df2 = df._append(df)
print(df2)

# loc で列を指定して取得
print(df.loc[:, "name"])  # Series
# 列を指定せず全部とってくる
print(df.loc[:, ])  # df.loc[:,:] でもよい
# loc で列を指定して Series を取得
print(df.loc[:, ["name", "age"]])
# boolean で指定 ( Series と連携して多用する )
print(df.loc[[True, False, True], ])

# iloc で index 指定して取得 -1,-2のように後ろから指定できる
print(df.iloc[-2:, ])
# ------------------------------
# 条件抽出
print(df['age'] < 25)  # Series
print(df[df['age'] < 25])  # DataFrame
# query で取得　(必ず新しいDFが返される)
print(df.query('age < 25'))  # DataFrame
value = 25
print(df.query('age < @value'))  # DataFrame (変数を参照する)

# 条件抽出して loc で抽出したindexを指定して "age"に値を代入
df_query = df.query('age > 15')
df.loc[df_query.index, "age"] = 100
# df.loc[df_query.index] = 100  # カラムを指定しない場合は全部書き変わる

# 文字列を含むデータを抽出
a_series = df['name'].str.contains('a')  # Seriesを取得 (bool一覧が返される)
a_df = df[df['name'].str.contains('a')]  # DataFrameに変換

print(df.loc[a_series])  # a_series で抽出
print(df.loc[a_df.index])  # index でも抽出できる
print(df.loc[~a_series])  # 抽出内容を~(NOT)演算子で反転