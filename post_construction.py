from functools import wraps


class FrozenInstanceError(AttributeError):

    pass


def deep_freeze(value):

    if isinstance(value, dict):
        return frozenset((deep_freeze(k), deep_freeze(v)) for k, v in value.items())

    elif isinstance(value, list):
        return tuple(deep_freeze(item) for item in value)

    elif isinstance(value, set):
        return frozenset(deep_freeze(item) for item in value)

    elif isinstance(value, tuple):
        return tuple(deep_freeze(item) for item in value)

    return value


def frozen(cls):

    original_init = cls.__init__

    def get_attributes(instance):

        attrs = {}

        if hasattr(instance, "__dict__"):
            attrs.update(instance.__dict__)

        slots = getattr(type(instance), "__slots__", ())

        if isinstance(slots, str):
            slots = (slots,)

        for slot in slots:

            if slot.startswith("__"):
                continue

            try:
                attrs[slot] = getattr(instance, slot)
            except AttributeError:
                pass

        return attrs

    @wraps(original_init)
    def new_init(self, *args, **kwargs):

        object.__setattr__(self, "_is_frozen", False)

        original_init(self, *args, **kwargs)

        attrs = get_attributes(self)

        for key, value in attrs.items():

            if key == "_is_frozen":
                continue

            frozen_value = deep_freeze(value)

            object.__setattr__(self, key, frozen_value)

        object.__setattr__(self, "_is_frozen", True)

    def frozen_setattr(self, key, value):

        if getattr(self, "_is_frozen", False):
            raise FrozenInstanceError(f"Cannot modify frozen instance: '{key}'")

        object.__setattr__(self, key, value)

    def frozen_delattr(self, key):

        if getattr(self, "_is_frozen", False):
            raise FrozenInstanceError(
                f"Cannot delete attribute from frozen instance: '{key}'"
            )

        object.__delattr__(self, key)

    def auto_hash(self):

        attrs = get_attributes(self)

        filtered = tuple(sorted((k, v) for k, v in attrs.items() if k != "_is_frozen"))

        return hash(filtered)

    cls.__init__ = new_init
    cls.__setattr__ = frozen_setattr
    cls.__delattr__ = frozen_delattr
    cls.__hash__ = auto_hash

    return cls


@frozen
class Person:

    def __init__(self, name, hobbies, metadata):

        self.name = name
        self.hobbies = hobbies
        self.metadata = metadata


p = Person(
    "Sayantan",
    ["coding", "music"],
    {"skills": ["Python", "C++"], "projects": {"AI", "ML"}},
)

print("Person Object Created")
print(p.name)
print(p.hobbies)
print(p.metadata)

print("\nHash Value:")
print(hash(p))

print("\nTrying mutation...")

try:
    p.name = "Raj"
except FrozenInstanceError as e:
    print("ERROR:", e)

try:
    p.hobbies.append("gaming")
except Exception as e:
    print("ERROR:", e)


@frozen
class Employee:

    __slots__ = ("id", "skills", "_is_frozen")

    def __init__(self, emp_id, skills):

        self.id = emp_id
        self.skills = skills


emp = Employee(101, ["Python", "System Design"])

print("\nEmployee Object Created")
print(emp.id)
print(emp.skills)

print("\nHash Value:")
print(hash(emp))

print("\nTrying mutation on slotted object...")

try:
    emp.id = 500
except FrozenInstanceError as e:
    print("ERROR:", e)

try:
    del emp.skills
except FrozenInstanceError as e:
    print("ERROR:", e)
