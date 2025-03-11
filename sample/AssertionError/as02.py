def area_circle(r):
    assert (r>=0), 'Radius Cannot be Less Than Zero!'
    return (((3.14)* r) * r)
print(area_circle(3))
x = -6
print(area_circle(x))