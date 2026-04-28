import functools
import csv
import os


class Pipeline:

    def __init__(self, generator):

        self._generator = generator

    def __iter__(self):

        return iter(self._generator)

    def pipe(self, stage, *args, **kwargs):

        return stage(self, *args, **kwargs)


def pipeline(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        if args and isinstance(args[0], Pipeline):

            source_iterable = args[0]._generator

            result = func(source_iterable, *args[1:], **kwargs)
            return Pipeline(result)
        else:

            result = func(*args, **kwargs)
            return Pipeline(result)

    def pipe_method(next_stage, *args, **kwargs):
        return wrapper().pipe(next_stage, *args, **kwargs)

    wrapper.pipe = pipe_method
    return wrapper


@pipeline
def csv_reader(iterable=None, filename=None):

    if filename is not None:

        with open(filename, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                yield row
    elif iterable is not None:

        for row in iterable:
            yield row
    else:
        raise ValueError("csv_reader needs either a filename or an input iterable")


@pipeline
def field_extractor(iterable, indices):

    for row in iterable:

        yield [row[i] for i in indices]


@pipeline
def type_converter(iterable, schema):

    for row in iterable:
        new_row = []
        for i, value in enumerate(row):
            if i in schema:

                new_row.append(schema[i](value))
            else:

                new_row.append(value)
        yield new_row


@pipeline
def batch_aggregator(iterable, batch_size):

    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


@pipeline
def explode(iterable, times=2):

    for item in iterable:
        for _ in range(times):
            yield item


@pipeline
def running_total(iterable, value_index=0):

    total = 0
    for row in iterable:
        total += row[value_index]

        yield row + [total]


if __name__ == "__main__":

    csv_content = """name,age,score
Sayantan,30,85.5
Deep,25,90.0
Anushka,35,78.5
Devdeep,28,92.0
"""

    with open("demo.csv", "w", newline="") as f:
        f.write(csv_content)

    result = (
        csv_reader(filename="demo.csv")
        .pipe(field_extractor, [0, 1, 2])
        .pipe(type_converter, {1: int, 2: float})
        .pipe(running_total, 2)
        .pipe(batch_aggregator, 2)
    )

    for batch in result:
        print(batch)

    flat = csv_reader(filename="demo.csv").pipe(field_extractor, [0]).pipe(explode, 3)

    for item in flat:
        print(item)

    os.remove("demo.csv")
