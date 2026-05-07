from abc import ABC, abstractmethod


class Employee(ABC):
    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id

    @abstractmethod
    def calculate_payroll(self):
        pass


class SalaryEmployee(Employee):
    def __init__(self, name: str, id: int, salary: float):
        Employee.__init__(self, name, id)
        self.salary = salary

    def calculate_payroll(self):
        return self.salary


class HourlyEmployee(Employee):
    def __init__(self, name: str, id: int, hourly_rate: float, hourly_time: float):
        super().__init__(name, id)
        self.hourly_rate = hourly_rate
        self.hourly_time = hourly_time

    def calculate_payroll(self):
        return self.hourly_rate * self.hourly_time


class CommisionEmployee(SalaryEmployee):
    def __init__(self, name: str, id: int, salary: float, commision: float):
        super().__init__(name, id, salary)
        self.commision = commision

    def calculate_payroll(self):
        fixed_salary = super().calculate_payroll()
        total_salary = fixed_salary + self.commision
        return total_salary


class RemoteEmployee(HourlyEmployee, SalaryEmployee):
    def __init__(
        self,
        name: str,
        id: int,
        salary: float,
        hourly_rate: float,
        hourly_time: float,
        contract_length: int = 1,
    ):
        Employee.__init__(self, name, id)
        self.salary = salary
        self.hourly_rate = hourly_rate
        self.hourly_time = hourly_time

        self.contract_length = contract_length

    def calculate_payroll(self):
        fixed_salary = super().calculate_payroll()
        hourly_salary = HourlyEmployee.calculate_payroll(self)
        return fixed_salary + hourly_salary


class PayRoll:
    def calculate_payroll(self, Employees):
        for employee in Employees:
            print(
                f"Name of employee is: {employee.name} and employee ID: {employee.id}\n Estimteed Salary of {employee.id}: {employee.calculate_payroll()}"
            )


class ManagerRole:
    def __init__(self, reports):
        self.reports = reports

    def get_report(self):
        return self.reports


class Manager(SalaryEmployee):
    def __init__(self, name: str, id: int, salary: float, reports: list):
        SalaryEmployee.__init__(self, name, id, salary)
        self.role = ManagerRole(reports)

    def get_report(self):
        return self.role.get_report()


class HourlyManager(HourlyEmployee):
    def __init__(
        self, name: str, id: int, hourly_rate: float, hourly_time: float, reports: list
    ):
        super().__init__(name, id, hourly_rate, hourly_time)
        self.role = ManagerRole(reports)

    def get_report(self):
        return self.role.get_report()


emp_salary = SalaryEmployee("Proloy", 4567, 12000)
emp_hourly = HourlyEmployee("Ankush", 1234, 500, 5.3)
emp_commision = CommisionEmployee("Rajesh", 9008, 30000, 2500)
emp_remote = RemoteEmployee("Sanjit", 4573, 45000, 570, 3, 2)
system = PayRoll()
print("Calculating total Esteemed Gross Salary of evry type Employee")

print(system.calculate_payroll([emp_salary, emp_hourly, emp_commision]))
manager = Manager("Sayantan", 9006, 50000, ["sayantan", "Debasish"])
print(manager.get_report())
print(manager.salary)
