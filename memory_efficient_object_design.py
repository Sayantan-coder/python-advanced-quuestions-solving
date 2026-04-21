class Point:
    __slots__ = ('x', 'y', '__weakref__')
    def __init__(self, x, y):
        self.x = x
        self.y = y


p = Point(2, 3)
print(p.x, p.y)  

try:
    p.z = 5
except AttributeError as e:
    print("Error:", e)
