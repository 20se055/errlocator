key = []
for i in range(1, 6):
    a = i
    b = a + 1
    key.append(i)
value = ["red", "green", "blue", "white", "black"]
d = dict(zip(key, value))

print(d[b])