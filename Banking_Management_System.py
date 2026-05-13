class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.__balance = balance

    # Getter Method to access the private Attribute:
    @property
    def balance(self):  # Get the current balance from the account
        return self.__balance

    # Setter Method to validate the value assign to private Attribute
    @balance.setter
    def balance(self, amount: float):
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount can not be other than int or float data type")
        if amount < 0:
            print("Amount can not be negative")
        else:
            self.__balance = amount
            print(f"balance is updated to:{amount} | Updated balance:{self.__balance}")

    @balance.deleter  # Delete Recorded Balance
    def balance(self):
        print("Delete recorded balance")
        del self.__balance

    def deposit(self, amount: float):
        if amount < 0:
            raise ValueError("Ammount less than 0 can not be deposited")
        else:
            self.__balance = self.__balance + amount
            print(f"{amount} is deposited | Updated balance is:{self.__balance}")

    def withdrawl(self, amount: float):
        if amount < 0:
            raise ValueError("Withdrawl amount can not be lesser than or equal to 0 ")
        else:
            self.__balance = self.__balance - amount
            print(
                f"{amount} is withdraw from account| Updated balance is:{self.__balance}"
            )


account = BankAccount("Sayantan", 340050)
print(account.balance)
account.balance = 50000
print(account.balance)
print(account.deposit(20000))
print(account.withdrawl(40000))
print(account.balance)
del account.balance
print(account.balance)
