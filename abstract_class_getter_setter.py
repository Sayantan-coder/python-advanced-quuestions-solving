from abc import ABC, abstractmethod


class Vehicle(ABC):
    @property
    @abstractmethod
    def fuel_type(self):
        pass

    @property
    @abstractmethod
    def max_speed(self):
        pass

    @property
    def get_brand(self):
        pass

    @property
    @abstractmethod
    def get_colour(self):
        pass


class ElectricCar(Vehicle):

    @property
    def fuel_type(self):
        return "Electric"

    @property
    def max_speed(self):
        return "250 km/hr"

    @property
    def get_colour(self):
        return "Read"

    @fuel_type.setter
    def fuel_type(self, new_type):
        self._new_type = new_type
        return self._new_type

    @max_speed.setter
    def max_speed(self, speed):
        if speed < 0:
            raise ValueError("Speed can not be negative")
        self._speed = speed
        return self._speed

    @get_colour.setter
    def get_colour(self, colour):
        self._colour = colour
        return self._colour


class Bike(Vehicle):
    @property
    def fuel_type(self):
        return "disel"

    @property
    def max_speed(self):
        return "120 km/hr."

    @property
    def get_colour(self):
        return "black"

    @get_colour.setter
    def get_colour(self, colour):
        self.new_colour = colour
        return self.new_colour


ec = ElectricCar()

bike = Bike()
print(ec.fuel_type)
print(ec.max_speed)
ec.max_speed = 75
print(ec.get_colour)

print(bike.fuel_type)
bike.get_colour = "blue"
print(bike.get_colour)
print(ec.max_speed)
ec.fuel_type = "Petrol"
print(ec.fuel_type)
