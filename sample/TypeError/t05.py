key = []
for i in range(1, 6):
    key.append(i)
value = ["red", "green", "blue", "white", "black"]
d = dict(zip(key, value))

print(d[key])