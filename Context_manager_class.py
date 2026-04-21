class suppress:
    def __init__(self, *exc_types):
        self.exc_types = exc_types
    def __enter__(self):
        
        pass
    def __exit__(self, exc_type, exc_val, exc_tb):
     
        return exc_type is not None and issubclass(exc_type, self.exc_types)


with suppress(ZeroDivisionError):
    print("Before division")
    result = 1 / 0  
    print("This won't print")
print("After block - program continues normally")
