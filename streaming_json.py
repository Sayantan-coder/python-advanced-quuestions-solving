import re


class StreamingJSONParser:

    def __init__(self, chunk_size=8192):

        self.chunk_size = chunk_size

        self.path_stack = []
        self.current_key = None

    def parse(self, filename):

        with open(filename, "r", encoding="utf-8") as f:

            buffer = ""

            in_string = False
            escape = False
            token = ""

            while True:

                chunk = f.read(self.chunk_size)

                if not chunk:
                    break

                buffer += chunk

                i = 0

                while i < len(buffer):

                    ch = buffer[i]

                    if in_string:

                        if escape:
                            token += ch
                            escape = False

                        elif ch == "\\":
                            escape = True

                        elif ch == '"':

                            in_string = False

                            yield ("string", token)

                            token = ""

                        else:
                            token += ch

                        i += 1
                        continue

                    if ch.isspace():
                        i += 1
                        continue

                    if ch == "{":
                        yield ("start_object", None)

                    elif ch == "}":
                        yield ("end_object", None)

                    elif ch == "[":
                        yield ("start_array", None)

                    elif ch == "]":
                        yield ("end_array", None)

                    elif ch == '"':
                        in_string = True

                    elif ch in "-0123456789":

                        num = ch
                        i += 1

                        while i < len(buffer) and buffer[i] in "0123456789.eE+-":
                            num += buffer[i]
                            i += 1

                        yield ("value", self._parse_number(num))

                        continue

                    elif buffer.startswith("true", i):

                        yield ("value", True)
                        i += 4
                        continue

                    elif buffer.startswith("false", i):

                        yield ("value", False)
                        i += 5
                        continue

                    elif buffer.startswith("null", i):

                        yield ("value", None)
                        i += 4
                        continue

                    elif ch == ":":
                        pass

                    elif ch == ",":
                        pass

                    i += 1

                buffer = ""

    def _parse_number(self, num):

        if "." in num or "e" in num or "E" in num:
            return float(num)

        return int(num)


class JSONSAXHandler:

    def __init__(self):

        self.stack = []
        self.current_key = None
        self.array_indices = []

    def process(self, events):

        expecting_key = False

        for event, value in events:

            if event == "start_object":

                self.stack.append("{")

                expecting_key = True

                yield ("start_object", None, self.current_path())

            elif event == "end_object":

                self.stack.pop()

                yield ("end_object", None, self.current_path())

            elif event == "start_array":

                self.stack.append("[")

                self.array_indices.append(0)

                yield ("start_array", None, self.current_path())

            elif event == "end_array":

                self.stack.pop()

                self.array_indices.pop()

                yield ("end_array", None, self.current_path())

            elif event == "string":

                if expecting_key:

                    self.current_key = value

                    yield ("key", value, self.current_path() + [value])

                    expecting_key = False

                else:

                    yield ("value", value, self.current_path())

                    expecting_key = True

            elif event == "value":

                yield ("value", value, self.current_path())

                expecting_key = True

    def current_path(self):

        path = []

        for item in self.stack:

            path.append(item)

        if self.current_key:
            path.append(self.current_key)

        return path


class JSONPathFilter:

    def __init__(self, expression):

        self.parts = self._parse_expression(expression)

    def _parse_expression(self, expr):

        expr = expr.replace("$.", "")

        parts = []

        for part in expr.split("."):

            if "[*]" in part:

                parts.append(part.replace("[*]", ""))
                parts.append("*")

            else:
                parts.append(part)

        return parts

    def matches(self, path):

        cleaned = []

        for p in path:

            if p not in ["{", "["]:
                cleaned.append(str(p))

        if len(cleaned) < len(self.parts):
            return False

        for a, b in zip(cleaned, self.parts):

            if b == "*":
                continue

            if a != b:
                return False

        return True


class CountAggregator:

    def __init__(self):
        self.count = 0

    def add(self, value):
        self.count += 1

    def result(self):
        return self.count


class SumAggregator:

    def __init__(self):
        self.total = 0

    def add(self, value):

        if isinstance(value, (int, float)):
            self.total += value

    def result(self):
        return self.total


class CollectAggregator:

    def __init__(self):
        self.items = []

    def add(self, value):
        self.items.append(value)

    def result(self):
        return self.items


class StreamingJSONQueryEngine:

    def __init__(self, filename):

        self.filename = filename

    def query(self, jsonpath, aggregator=None):

        parser = StreamingJSONParser()

        sax = JSONSAXHandler()

        matcher = JSONPathFilter(jsonpath)

        events = parser.parse(self.filename)

        for event, value, path in sax.process(events):

            if event == "value":

                if matcher.matches(path):

                    if aggregator:
                        aggregator.add(value)

                    else:
                        yield value

        if aggregator:
            yield aggregator.result()


if __name__ == "__main__":

    engine = StreamingJSONQueryEngine("massive.json")

    print("Cities:")

    for city in engine.query("$.users[*].address.city"):
        print(city)

    count_agg = CountAggregator()

    result = list(engine.query("$.users[*].address.city", aggregator=count_agg))

    print("Count:", result[0])

    sum_agg = SumAggregator()

    result = list(engine.query("$.transactions[*].amount", aggregator=sum_agg))

    print("Total Amount:", result[0])
