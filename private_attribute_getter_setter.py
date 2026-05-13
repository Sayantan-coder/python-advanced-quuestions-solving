class Employee:
    def __init__(self, name: str, age: int, salary: float):
        self.name = name
        self._age = age
        self.__salary = salary

    def get_sallary(self):  # Getter method to access the private property
        return self.__salary

    def set_sallary(
        self, amount: float
    ):  # setter method to modify the Private property
        if amount < 0:
            print("Salary can not be less than zero")
        elif amount > 1000000:
            print("Salary is too high, Please check the input amount")
        else:
            self.__salary = amount
            print(f"Salary is Updated to:{amount}")


emp = Employee("Sayantan", 23, 40007)
emp1 = Employee("Sayantan", 21, 50000000)
print(emp1.get_sallary())
print(emp1.__dict__)
print(emp.get_sallary())
print(emp1.set_sallary(234))
print(emp._Employee__salary)
print(emp1._age)
print(emp.__salary)
