class Base:
    def process(self):
        print("Base processing")


class LoggingMixin(Base):
    def process(self):
        print(f"Log in: Logging starts before processing")
        super().process()
        print(f"Log in: Logging starts after processing")


class CacheMixin(Base):
    def process(self):
        print(f"CacheMixin: Cache Checking")
        super().process()
        print(f"CacheMixin: Updating Cache")


class TimerMixin(Base):
    def process(self):
        print(f"TimerMixin:Starting timer")
        super().process()
        print(f"TimerMixin: Stopping timer")


class DataHandeler(LoggingMixin, CacheMixin, TimerMixin, Base):
    def process(self):
        print(f"DataHandeler: Core Logic running")
        super().process()


dh = DataHandeler()
dh.process()
