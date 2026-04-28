from typing import get_origin, get_args, Union, Optional, List


def auto_properties(cls):
    annotations = cls.__annotations__

    for attr, expected_type in annotations.items():
        private_name = "_" + attr

        def getter(self, name=private_name):
            return getattr(self, name, None)

        def setter(self, value, name=private_name, typ=expected_type):
            if not check_type(value, typ):
                raise TypeError(f"{name[1:]} must be {typ}")
            setattr(self, name, value)

        setattr(cls, attr, property(getter, setter))

    return cls


def check_type(value, typ):
    origin = get_origin(typ)
    args = get_args(typ)

    if origin is Union:
        return any(check_type(value, t) for t in args)

    if value is None:
        return typ is type(None)

    if origin is list:
        if not isinstance(value, list):
            return False
        return all(check_type(v, args[0]) for v in value)

    return isinstance(value, typ)


@auto_properties
class Person:
    name: str
    age: int
    scores: List[int]
    nickname: Optional[str]

    def __init__(self, name, age, scores, nickname=None):
        self.name = name
        self.age = age
        self.scores = scores
        self.nickname = nickname


p = Person("Sayantan", 23, [90, 85, 88])

print(p.name)
print(p.age)
print(p.scores)
print(p.nickname)

p.age = 27
p.nickname = "Deep"
p.scores = [100, 95]
