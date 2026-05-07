class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def get_pay(self):
        return self.salary


class FullTimeEmployee(Employee):
    def __init__(self, name, salary, benefits=0):
        super().__init__(name, salary)
        self.benefits = benefits

    def get_pay(self):

        return self.salary + self.benefits


class ContractEmployee(Employee):
    def __init__(self, name, salary, contract_length=1):
        super().__init__(name, salary)
        self.contract_length = contract_length

    def get_pay(self):

        return self.salary


class Manager(FullTimeEmployee, ContractEmployee):
    def __init__(self, name, salary, benefits, contract_length, bonus):
        Employee.__init__(self, name, salary)
        self.benefits = benefits
        self.contract_length = contract_length
        self.bonus = bonus

        # super().__init__(name, salary, benefits)
        # self.bonus = bonus

    def get_pay(self):
        base = super().get_pay()
        return base + self.bonus


mgr = Manager("Sayantan", salary=16000, benefits=2500, contract_length=12, bonus=1000)
print(f"{mgr.name} total payment is: {mgr.get_pay()}")
