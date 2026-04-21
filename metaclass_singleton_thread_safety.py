import threading

class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class Logger(metaclass=SingletonMeta):
    def __init__(self):
        self.logs = []

    def log(self, msg):
        self.logs.append(msg)

log1 = Logger()
log2 = Logger()
log1.log("First message")
log2.log("Second message")
print(log1.logs)   
print(log1 is log2)  
