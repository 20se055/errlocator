try:
	a = 100/10
	raise Exception('例外のテスト','err1')

except Exception as e:
	print(e) # ('例外のテスト','err1')