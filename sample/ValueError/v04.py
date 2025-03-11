def sum(n):
    s = 0
    x = 0
    for i in range(1, n + 1, x):
        s += i
    return s

x = int(input("num: "))
print(sum(x))
