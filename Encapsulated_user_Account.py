from datetime import datetime


class UserAccount:

    _MIN_PASSWORD_LENGTH = 8  # Class-level Protected Attribute

    def __init__(self, username, email, password):
        self.__username = username  # Username is Private Attribute
        self.__email = email  # email is private Attribute
        self.__password_hash = self.__hash_password(password)  # private method
        self.__login_count = 0
        self.__created_at = datetime.now()
        self.__is_active = True

    def __hash_password(self, password):

        return f"hashed_{hash(password)}"

    def __validate_email(self, email):
        return "@" in email and "." in email

    @property
    def username(self):
        return self.__username

    @property
    def created_at(self):
        return self.__created_at.strftime("%Y-%m-%d %H:%M")

    @property
    def login_count(self):
        return self.__login_count

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, new_email):
        if not self.__validate_email(new_email):
            raise ValueError(f" Invalid email: {new_email}")
        self.__email = new_email
        print(f" Email updated to: {new_email}")

    @property
    def account_age_days(self):
        return (datetime.now() - self.__created_at).days

    @property
    def is_active(self):
        return self.__is_active

    @is_active.setter
    def is_active(self, status):
        if not isinstance(status, bool):
            raise TypeError("Status must be True or False")
        self.__is_active = status

    def login(self, password):
        if not self.__is_active:
            return " Account is deactivated."
        if self.__hash_password(password) == self.__password_hash:
            self.__login_count += 1
            return f" Welcome back, {self.__username}! (Login #{self.__login_count})"
        return " Incorrect password."

    def change_password(self, old_password, new_password):
        if self.__hash_password(old_password) != self.__password_hash:
            return " Old password is incorrect."
        if len(new_password) < self._MIN_PASSWORD_LENGTH:
            return f" Password must be at least {self._MIN_PASSWORD_LENGTH} characters."
        self.__password_hash = self.__hash_password(new_password)
        return " Password changed successfully."

    def __str__(self):
        status = "Active" if self.__is_active else "Inactive"
        return (
            f" {self.__username} | {self.__email} | "
            f"Status: {status} | Joined: {self.created_at}"
        )


user = UserAccount("Rajdeep", "Rajdeep@gmail.com", "secure@123")

print(user)
print(user.login("secure@123"))
print(user.login("wrong_pass"))

user.email = "Monadal@outlook.com"
# user.email = "not-an-email"

print(user.change_password("secure@123", "ab"))
print(user.change_password("secure@123", "newpassword@456"))

user.is_active = False
print(user.login("newpassword@456"))

# print(user.__password_hash)
