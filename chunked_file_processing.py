import mmap
import os
import struct
from multiprocessing import pool, cpu_count
import random, time, string

Magic = b"\xde\xad\xbe\xef"
Magic_number = 0xDEADBEEF
Payload_Timestamp_Offset = 0
Payload_LogLevel_Offset = 8
Payload_Message_Offset = 9
Header_size = 6
Log_level = {0: "DEBUG", 1: "INFO", 2: "WARN", 3: "ERROR"}


def _Worker_Scan_Region(filepath, start_offset, end_offset):
    entries = []
    with open(filepath, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        file_size = len(mm)
        offset = start_offset
        while offset < end_offset and offset < (file_size - Header_size):
            current = mm[offset : offset + 4]
            if current == Magic:
                if offset + Header_size > file_size:
                    break
                length = struct.unpack_from(">H", mm, offset + 4)[0]
                if offset + Header_size + length <= file_size:
                    payload = bytes(
                        mm[offset + Header_size : offset + Header_size + length]
                    )
                    entry = _parse_payload(offset, length, payload)
                    entries.append(entry)
                    offset = offset + Header_size + length
                else:
                    offset += 1
            else:
                offset = offset + 1
        mm.close()
    return entries


def _parse_payload(offset, length, payload):
    entry = {"offset": offset, "length": length, "raw": payload}
    if len(payload) >= 9:
        timestamp = struct.unpack_from(">d", payload, Payload_Timestamp_Offset)[0]
        log_level = struct.unpack_from(">B", payload, Payload_LogLevel_Offset)[0]
        message = payload[Payload_Message_Offset:].decode("utf-8", errors="replace")
        entry["timestamp"] = timestamp
        entry["log_level"] = log_level
        entry["log_level_name"] = Log_level.get(log_level, f"Level{log_level}")
        entry["message"] = message
    else:
        entry["timestamp"] = None
        entry["log_level"] = None
        entry["log_level_name"] = "Unknown"
        entry["message"] = payload.decode("utf-8", errors="replace")
    return entry


class LogFileProcessor:
    def __init__(self, file_path, chunk_size=4096):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self._file = None
        self._mm = None

    def __enter__(self):
        self._file = open(self.file_path, "r+b")
        self._mm = mmap.mmap(self._file.fileno(), 0)
        print(
            f"[LogFileProcessor] Opened '{self.filepath}' "
            f"({len(self._mm):,} bytes mapped)"
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._mm:
            self._mm.flush()
            self._mm.close()
        if self._file:
            self._file.close()
        print("[LogFileProcessor] Closed and flushed.")
        return False

    def _check_open(self):
        if self._mm is None:
            raise RuntimeError(
                "LogFileProcessor must be used as a context manager: "
                "`with LogFileProcessor(...) as lp:`"
            )

    def scan(self):
        self._check_open()
        entries = []
        file_size = len(self._mm)
        offset = 0
        while offset <= file_size - Header_size:
            chunk_end = min(offset + self.chunk_size, file_size)
            chunk = self._mm[offset:chunk_end]
            position = chunk.find(Magic)
            if position != -1:
                abs_offset = offset + position
                if abs_offset + Header_size > file_size:
                    break
                length = struct.unpack_from(">H", self._mm, abs_offset + 4)[0]
                if abs_offset + Header_size + length <= file_size:
                    payload = bytes(
                        self._mm[
                            abs_offset + Header_size : abs_offset + Header_size + length
                        ]
                    )
                    entry = _parse_payload(abs_offset, length, payload)
                    entries.append(entry)
                    offset = abs_offset + Header_size + length
                else:
                    break
            else:
                offset = offset + max(1, self.chunk_size - 3)
        print(f"[scan] Found {len(entries)} log entries.")
        return entries

    def read_entry(self, offset):
        self._check_open()
        file_size = len(self._mm)
        if offset < 0 or offset + Header_size > file_size:
            raise ValueError(
                f"Offset {offset} is out of bounds (file size={file_size})."
            )
        magic = bytes(self._mm[offset : offset + 4])
        if magic != Magic:
            raise ValueError(
                f"No valid magic number at offset {offset}. "
                f"Got {magic.hex()} expected {Magic.hex()}."
            )
        length = struct.unpack_from(">H", self._mm, offset + 4)[0]
        if offset + Header_size + length > file_size:
            raise ValueError(f"Entry at offset {offset} is truncated (file too short).")
        payload = bytes(self._mm[offset + Header_size : offset + Header_size + length])
        return _parse_payload(offset, length, payload)


if __name__ == "__main__":
    main()
