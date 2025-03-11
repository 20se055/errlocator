import os, glob

# 条件に合うファイルパス情報をすべて取得
file_list = glob.glob('plugin/*.py')
# パス情報からファイル名だけを取り出す
__all__ = [os.path.splitext(os.path.basename(file))[0] for file in file_list]
# __all__ =  ['value_1']