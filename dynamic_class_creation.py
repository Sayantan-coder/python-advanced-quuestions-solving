def class_factory(class_name, field_names):

    attrs = {}

    def __init__(self, **kwargs):
        for field in field_names:
            setattr(self, field, kwargs.get(field))

    attrs["__init__"] = __init__

    return type(class_name, (object,), attrs)


Person = class_factory("Person", ["name", "age"])
p = Person(name="Deep", age=24)
print(p.name, p.age)
