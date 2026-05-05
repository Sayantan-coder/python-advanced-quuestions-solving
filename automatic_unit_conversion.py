from functools import wraps


class IncompatibleUnitsError(Exception):
    pass


class UnitConverter:
    def __init__(self):
        self.registry = {}

    def register(self, unit, category, to_base, from_base, is_base=False):
        self.registry[unit] = {
            "category": category,
            "to_base": to_base,
            "from_base": from_base,
            "is_base": is_base,
        }

    def get_category(self, unit):
        return self.registry[unit]["category"]

    def get_base_unit(self, unit):
        category = self.get_category(unit)
        for u, data in self.registry.items():
            if data["category"] == category and data["is_base"]:
                return u
        raise ValueError(f"No base unit defined for category {category}")

    def convert(self, value, from_unit, to_unit):
        if from_unit == to_unit or to_unit is None:
            return value

        u1 = self.registry[from_unit]
        u2 = self.registry[to_unit]

        if u1["category"] != u2["category"]:
            raise IncompatibleUnitsError(f"Cannot convert {from_unit} to {to_unit}")

        base_value = u1["to_base"](value)

        return u2["from_base"](base_value)


converter = UnitConverter()


converter.register("meters", "length", lambda x: x, lambda x: x, is_base=True)

converter.register("km", "length", lambda x: x * 1000, lambda x: x / 1000)

converter.register("miles", "length", lambda x: x * 1609.34, lambda x: x / 1609.34)


converter.register("celsius", "temperature", lambda x: x, lambda x: x, is_base=True)

converter.register(
    "fahrenheit", "temperature", lambda x: (x - 32) * 5 / 9, lambda x: (x * 9 / 5) + 32
)


def unit_aware(func):
    @wraps(func)
    def wrapper(*args, output_unit=None, **kwargs):
        annotations = func.__annotations__

        converted_args = []
        arg_names = [k for k in annotations.keys() if k != "return"]

        for i, arg in enumerate(args):
            name = arg_names[i]

            unit = annotations.get(name)
            base_unit = converter.get_base_unit(unit)

            converted_value = converter.convert(arg, unit, base_unit)
            converted_args.append(converted_value)

        result = func(*converted_args, **kwargs)

        return_unit = annotations.get("return")

        if return_unit is None:
            return result

        base_unit = converter.get_base_unit(return_unit)

        if isinstance(result, tuple):
            if output_unit is None:
                return result

            return tuple(converter.convert(r, base_unit, output_unit) for r in result)

        if output_unit:
            return converter.convert(result, base_unit, output_unit)

        return result

    return wrapper


@unit_aware
def add_distance(a: "km", b: "meters") -> "meters":
    return a + b


@unit_aware
def temperature_difference(t1: "celsius", t2: "fahrenheit") -> "celsius":
    return t1 - t2


@unit_aware
def scale_and_sum(x: "meters", y: "meters") -> "meters":
    return x * 2, x + y


if __name__ == "__main__":

    print(add_distance(1, 500, output_unit="km"))

    print(temperature_difference(100, 32))

    print(scale_and_sum(1000, 2000, output_unit="km"))

    second_output_km = scale_and_sum(1000, 1000, output_unit="km")[1]
    result = add_distance(second_output_km, 500, output_unit="km")
    print(result)

    try:
        print(add_distance(1, 100, output_unit="celsius"))
    except IncompatibleUnitsError as e:
        print("Error:", e)
