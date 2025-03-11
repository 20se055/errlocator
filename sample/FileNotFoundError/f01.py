filename = "test.txt"

with open(filename, 'r') as file:
    print(file.read())
        
# except IOError:
#     print(f"ファイル '{filename}' が見つかりませんでした。")