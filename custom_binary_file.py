import struct
import os
import bisect


class BinaryTableFile:

    MAGIC = b"BTBL"
    VERSION = 1

    TYPE_INT32 = 1
    TYPE_FLOAT64 = 2
    TYPE_BOOL = 3
    TYPE_STRING = 4

    TYPE_MAP = {
        "int32": TYPE_INT32,
        "float64": TYPE_FLOAT64,
        "bool": TYPE_BOOL,
        "string": TYPE_STRING,
    }

    STRUCT_MAP = {TYPE_INT32: "i", TYPE_FLOAT64: "d", TYPE_BOOL: "?"}

    HEADER_FORMAT = "<4sIIIIII"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    SCHEMA_FORMAT = "<32sBI"
    SCHEMA_SIZE = struct.calcsize(SCHEMA_FORMAT)

    INDEX_ENTRY_FORMAT = "<ii"

    def __init__(self, filename, schema, index_field=None):

        self.filename = filename
        self.schema = schema
        self.index_field = index_field

        self.fields = []
        self.record_size = 0

        self.index = []

        self._compute_layout()

        if not os.path.exists(filename):
            self._initialize_file()

    def _compute_layout(self):

        offset = 0

        for name, dtype in self.schema:

            if dtype == "int32":
                size = 4

            elif dtype == "float64":
                size = 8

            elif dtype == "bool":
                size = 1

            elif dtype == "string":
                size = 8  # offset + length

            else:
                raise ValueError("Unsupported type")

            self.fields.append({"name": name, "type": dtype, "offset": offset})

            offset += size

        self.record_size = offset

    def _initialize_file(self):

        with open(self.filename, "wb") as f:

            schema_offset = self.HEADER_SIZE
            data_offset = schema_offset + len(self.fields) * self.SCHEMA_SIZE

            header = struct.pack(
                self.HEADER_FORMAT,
                self.MAGIC,
                self.VERSION,
                0,
                schema_offset,
                data_offset,
                0,
                0,
            )

            f.write(header)

            for field in self.fields:

                name_bytes = field["name"].encode().ljust(32, b"\x00")

                type_id = self.TYPE_MAP[field["type"]]

                packed = struct.pack(
                    self.SCHEMA_FORMAT, name_bytes, type_id, field["offset"]
                )

                f.write(packed)

    def _read_header(self):

        with open(self.filename, "rb") as f:

            raw = f.read(self.HEADER_SIZE)

            return struct.unpack(self.HEADER_FORMAT, raw)

    def _write_header(
        self, record_count, schema_offset, data_offset, heap_offset, index_offset
    ):

        with open(self.filename, "r+b") as f:

            header = struct.pack(
                self.HEADER_FORMAT,
                self.MAGIC,
                self.VERSION,
                record_count,
                schema_offset,
                data_offset,
                heap_offset,
                index_offset,
            )

            f.seek(0)
            f.write(header)

    def _append_string(self, value):

        value_bytes = value.encode()

        with open(self.filename, "ab") as f:

            offset = f.tell()

            f.write(value_bytes)

            return offset, len(value_bytes)

    def _read_string(self, offset, length):

        with open(self.filename, "rb") as f:

            f.seek(offset)

            return f.read(length).decode()

    def write_record(self, record):

        header = self._read_header()

        _, _, record_count, schema_offset, data_offset, heap_offset, index_offset = (
            header
        )

        packed_record = b""

        for field in self.fields:

            name = field["name"]
            dtype = field["type"]

            value = record[name]

            if dtype == "int32":

                packed_record += struct.pack("<i", value)

            elif dtype == "float64":

                packed_record += struct.pack("<d", value)

            elif dtype == "bool":

                packed_record += struct.pack("<?", value)

            elif dtype == "string":

                offset, length = self._append_string(value)

                packed_record += struct.pack("<II", offset, length)

        with open(self.filename, "r+b") as f:

            record_pos = data_offset + record_count * self.record_size

            f.seek(record_pos)

            f.write(packed_record)

        if self.index_field:

            key = record[self.index_field]

            bisect.insort(self.index, (key, record_count))

        record_count += 1

        self._write_header(
            record_count, schema_offset, data_offset, heap_offset, index_offset
        )

    def read_record(self, index):

        header = self._read_header()

        _, _, record_count, _, data_offset, _, _ = header

        if index >= record_count:
            raise IndexError("Record index out of range")

        with open(self.filename, "rb") as f:

            pos = data_offset + index * self.record_size

            f.seek(pos)

            raw = f.read(self.record_size)

        result = {}

        cursor = 0

        for field in self.fields:

            name = field["name"]
            dtype = field["type"]

            if dtype == "int32":

                value = struct.unpack_from("<i", raw, cursor)[0]

                cursor += 4

            elif dtype == "float64":

                value = struct.unpack_from("<d", raw, cursor)[0]

                cursor += 8

            elif dtype == "bool":

                value = struct.unpack_from("<?", raw, cursor)[0]

                cursor += 1

            elif dtype == "string":

                offset, length = struct.unpack_from("<II", raw, cursor)

                value = self._read_string(offset, length)

                cursor += 8

            result[name] = value

        return result

    def read_all(self):

        header = self._read_header()

        record_count = header[2]

        return [self.read_record(i) for i in range(record_count)]

    def update_record(self, index, new_record):

        header = self._read_header()

        _, _, record_count, _, data_offset, _, _ = header

        if index >= record_count:
            raise IndexError("Invalid record index")

        packed_record = b""

        for field in self.fields:

            name = field["name"]
            dtype = field["type"]

            value = new_record[name]

            if dtype == "int32":

                packed_record += struct.pack("<i", value)

            elif dtype == "float64":

                packed_record += struct.pack("<d", value)

            elif dtype == "bool":

                packed_record += struct.pack("<?", value)

            elif dtype == "string":

                offset, length = self._append_string(value)

                packed_record += struct.pack("<II", offset, length)

        with open(self.filename, "r+b") as f:

            pos = data_offset + index * self.record_size

            f.seek(pos)

            f.write(packed_record)

    def lookup_by_index(self, value):

        keys = [k for k, _ in self.index]

        pos = bisect.bisect_left(keys, value)

        if pos >= len(self.index):
            return None

        if self.index[pos][0] != value:
            return None

        record_index = self.index[pos][1]

        return self.read_record(record_index)


if __name__ == "__main__":

    schema = [
        ("id", "int32"),
        ("temperature", "float64"),
        ("active", "bool"),
        ("name", "string"),
    ]

    table = BinaryTableFile("scientific_data.bin", schema, index_field="id")

    table.write_record(
        {"id": 1, "temperature": 23.5, "active": True, "name": "sensorA"}
    )

    table.write_record(
        {"id": 2, "temperature": 19.8, "active": False, "name": "sensorB"}
    )

    print(table.read_record(0))

    print(table.read_all())

    print(table.lookup_by_index(2))

    table.update_record(
        1, {"id": 2, "temperature": 30.1, "active": True, "name": "updatedSensor"}
    )

    print(table.read_record(1))
