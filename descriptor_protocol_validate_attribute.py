class NonNegative:
    def __set_name__(self, owner, name):
        self.private_name = "_" + name  

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name, 0)

    def __set__(self, obj, value):
        if value < 0:
            raise ValueError(f"Negative value not allowed: {value}")
        setattr(obj, self.private_name, value)

class Account:
    balance = NonNegative()

    def __init__(self, balance):
        self.balance = balance  


acc = Account(100)
print(acc.balance)   
try:
    acc.balance = -50
except ValueError as e:
    print("Error:", e)
