import json
import datetime


class SerializableMixin:
    def to_json(self):
        return json.dumps(self.__dict__, default=str)


class LoggingMixin:
    def to_log(self):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {self.__class__.__name__}:{self.__dict__}"


class ValidationMixin:
    def to_validate(self):
        for key, value in self.__dict__.items():
            if value is None:
                print(f"Field {key} is not valid")
        return f"{self.__class__.__name__} is valid"


class User(SerializableMixin, LoggingMixin, ValidationMixin):
    def __init__(self, name: str, age: int, e_mail: str):
        self.name = name
        self.age = age
        self.e_mail = e_mail


user = User("Sayantan", 23, "abc@gmail.com")
print(user.to_log())
print(user.to_validate())
print(user.to_json())
print(user.name)
print(user.age)
print(user.e_mail)
