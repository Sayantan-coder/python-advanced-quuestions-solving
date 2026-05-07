class Account:
    def __init__(self, name: str, account_number: int, age: int, amount: float):
        self.name = name
        self.account_number = account_number
        self.age = age
        self.amount = amount

    def deposite_money(self, deposite_amount: float):
        total_amount = self.amount + deposite_amount
        return total_amount

    def withdrawl_money(self, withdrawl_amount: float):
        amount = self.amount - withdrawl_amount
        return amount


account1 = Account("Sayantan", 5173120000217, 23, 60000)
print(account1.deposite_money(5000))
print(account1.withdrawl_money(3000))
