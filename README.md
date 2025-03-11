# errlocator
プログラム実行時に発生したエラーの原因分析を支援する手法
このツールでは，エラーメッセージからエラーに関連する変数を抽出し，その変数を基にソースコードに対しスライシングを行うことで修正が必要な可能性のある箇所を提示します．

## errlocatorを動作させるために必要なもの
+ pandas numpy pymysql
+ mysql
+ setup.pyにsqlの情報入力

## 使用方法
1. MySQLを起動
2. `$ cd tool`
3. `$ python3 ./errlocator path/to/file.py [-a]`

[-a] プロジェクトの実行に引数が必要な場合：

`$ python3 ./errlocator path/to/file.py -a arg1 arg2`

## 実行例
```python
$ python3 /path/to/sites.py -a user123
Traceback (most recent call last):
  File "/path/to/sites.py", line 232, in <module>
    sites_info = SitesInformation()
                 ^^^^^^^^^^^^^^^^^^
  File "/path/to/sites.py", line 165, in __init__
    site_data[site_name]["urlMain"],
    ~~~~~~~~~^^^^^^^^^^^
KeyError: 'XXX'
--------------------------------------------------
Cause of error:
/path/to/sites.py
144:   try:
145:     site_data = json.load(file)  #suspicious point
~~~
159: for site_name in site_data:
160:   site_name = "XXX"  #suspicious point
161:   #try:
162:
163:   self.sites[site_name] = n
164:     SiteInformation(site_name,
165:       site_data[site_name] ["urlMain"],  #suspicious point
166:       site_data[site_name]["url"],
167:       site_data[site_name]["username_claimed"],
168:       site_data[site_name],
169:       site_data[site_name].get("isNSFW",False)
170:
171:     )
172:   #except KeyError as error:
173:   # raise ValueError(
174:   # f"Problem parsing json contents at `data_file_path': Missing attribute error."
175:   # )
```
※実際には#suspicious pointと書いた箇所にマーカーが付いた状態で出力される
