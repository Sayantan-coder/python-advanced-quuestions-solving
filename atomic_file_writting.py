import os
import json
import hashlib
import tempfile
import shutil
from contextlib import contextmanager

if os.name == "nt":
    import msvcrt
else:
    import fcntl


class FileLock:

    def __init__(self, file_obj):
        self.file_obj = file_obj

    def acquire(self):
        if os.name == "nt":
            msvcrt.locking(self.file_obj.fileno(), msvcrt.LK_LOCK, 1)
        else:
            fcntl.flock(self.file_obj.fileno(), fcntl.LOCK_EX)

    def release(self):
        if os.name == "nt":
            msvcrt.locking(self.file_obj.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(self.file_obj.fileno(), fcntl.LOCK_UN)


class JournalManager:

    JOURNAL_FILE = "atomic_writer.journal"

    @classmethod
    def load(cls):
        if not os.path.exists(cls.JOURNAL_FILE):
            return []

        with open(cls.JOURNAL_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def save(cls, entries):
        with open(cls.JOURNAL_FILE, "w") as f:
            json.dump(entries, f, indent=4)

    @classmethod
    def add_entry(cls, entry):
        entries = cls.load()
        entries.append(entry)
        cls.save(entries)

    @classmethod
    def remove_entry(cls, temp_path):
        entries = cls.load()
        entries = [e for e in entries if e["temp_path"] != temp_path]
        cls.save(entries)

    @classmethod
    def recover(cls):
        entries = cls.load()

        for entry in entries:
            temp_path = entry["temp_path"]
            target_path = entry["target_path"]

            if os.path.exists(temp_path):
                try:
                    os.replace(temp_path, target_path)
                    print(f"Recovered: {target_path}")
                except Exception:
                    print(f"Failed recovery: {target_path}")

        cls.save([])


class AtomicFileWriter:

    CHECKSUM_SEPARATOR = b"\n===SHA256===\n"

    def __init__(self, target_path):
        self.target_path = target_path
        self.directory = os.path.dirname(target_path) or "."
        self.temp_path = None

    def _compute_checksum(self, data):
        return hashlib.sha256(data).hexdigest().encode()

    def _verify_file(self, temp_path):
        with open(temp_path, "rb") as f:
            content = f.read()

        data, checksum = content.split(self.CHECKSUM_SEPARATOR)

        expected = self._compute_checksum(data)

        return expected == checksum

    def write(self, data: bytes):
        fd, self.temp_path = tempfile.mkstemp(dir=self.directory, prefix=".tmp_")

        try:
            with os.fdopen(fd, "wb") as f:
                lock = FileLock(f)
                lock.acquire()

                checksum = self._compute_checksum(data)

                f.write(data)
                f.write(self.CHECKSUM_SEPARATOR)
                f.write(checksum)

                f.flush()
                os.fsync(f.fileno())

                lock.release()

            if not self._verify_file(self.temp_path):
                raise ValueError("Checksum verification failed.")

            JournalManager.add_entry(
                {"target_path": self.target_path, "temp_path": self.temp_path}
            )

            self._safe_replace(self.temp_path, self.target_path)

            JournalManager.remove_entry(self.temp_path)

        except Exception:
            self.rollback()
            raise

    def rollback(self):
        if self.temp_path and os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def _safe_replace(self, src, dst):

        try:
            os.replace(src, dst)

        except OSError:

            temp_copy = dst + ".copytmp"

            shutil.copy2(src, temp_copy)

            with open(temp_copy, "rb") as f:
                os.fsync(f.fileno())

            os.replace(temp_copy, dst)

            os.remove(src)


class TransactionContext:

    def __init__(self):
        self.operations = []

    def add_operation(self, writer, data):
        self.operations.append((writer, data))

    def commit(self):
        completed = []

        try:
            for writer, data in self.operations:
                writer.write(data)
                completed.append(writer)

        except Exception as e:
            print("Transaction failed. Rolling back...")

            for writer in completed:
                writer.rollback()

            raise e

    def rollback(self):
        for writer, _ in self.operations:
            writer.rollback()


if __name__ == "__main__":

    JournalManager.recover()

    writer = AtomicFileWriter("example.txt")

    writer.write(b"Hello Atomic World!")

    print("Single file write successful.")

    tx = TransactionContext()

    writer1 = AtomicFileWriter("file1.txt")
    writer2 = AtomicFileWriter("file2.txt")

    tx.add_operation(writer1, b"Data for file1")
    tx.add_operation(writer2, b"Data for file2")

    tx.commit()

    print("Transaction successful.")
