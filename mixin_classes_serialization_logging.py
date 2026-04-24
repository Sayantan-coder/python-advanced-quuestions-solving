import json


class SerializableMixin:
    def to_json(self):

        return json.dumps(self.__dict__)


class LoggingMixin:
    def log(self, msg):
        print(f"[LOG] {msg}")


class User(SerializableMixin, LoggingMixin):
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def display(self):
        self.log(f"User: {self.username}, Email: {self.email}")


u = User("Sayantan", "Sayantan@gmail.com")
print(u.to_json())
u.display()
