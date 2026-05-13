class Hospital:
    hospital_name = "IQ City Hospital"

    def __init__(self, patient: str, diagonosis: str, salary: float):
        self.patient = patient
        self._diagonosis = diagonosis
        self.__salary = salary

    # Getter method to access the Private Attribute
    @property
    def salary(self):
        return f"{self.__salary} per month"

    @salary.setter
    def salary(self, amount: float):
        if amount < 20000:
            raise ValueError("Salary can not be less than 20,000")
        else:
            self.__salary = amount
            return f"Salary amount:{self.__salary}"

    def _generate_report(self):
        return f"[Internal Report]:{self.patient} |{self._diagonosis}"

    def __validate_patient(self):
        return len(self.patient) > 0

    def admit_patient(self):
        if self.__validate_patient():
            return f"{self.patient} is succesfully is admitted with {self._diagonosis}"


class Surgeon(Hospital):
    def full_report(self):
        base_report = super()._generate_report()
        return f"  {base_report}|{self.salary}"


h = Hospital("Diya", "Tumor", 34000)
print(h.patient)
print(h.salary)
h.salary = 45000
print(h.salary)
print(h._generate_report())
print(h.admit_patient())
print(h._diagonosis)
s = Surgeon("Anushka", "Alergie", 150000)
print(s.full_report())
