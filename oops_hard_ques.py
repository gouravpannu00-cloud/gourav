         #  QUES 1 ______________________________________

class Employee:
    def __init__(self, name):
        self.name = name

    def work(self):
        print(self.name, "is working")


class Developer(Employee):
    def work(self):
        print(self.name, "is writing code")


class Designer(Employee):
    def work(self):
        print(self.name, "is designing UI")


class Manager(Employee):
    def work(self):
        print(self.name, "is managing the team")


employees = [
    Developer("Gourav"),
    Designer("Vansh"),
    Manager("Amit")
]

for employee in employees:
    employee.work()


     #   QUES    2  _______________________________
    
from abc import ABC, abstractmethod


class Payment(ABC):
    def __init__(self, amount):
        self.amount = amount

    @abstractmethod
    def pay(self):
        pass


class UPI(Payment):
    def pay(self):
        print("Paid ₹", self.amount, "using UPI")


class CreditCard(Payment):
    def pay(self):
        print("Paid ₹", self.amount, "using Credit Card")


class NetBanking(Payment):
    def pay(self):
        print("Paid ₹", self.amount, "using Net Banking")


payments = [
    UPI(500),
    CreditCard(1000),
    NetBanking(1500)
]

for payment in payments:
    payment.pay()


     #  QUES    3 _____________________________________
     
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display(self):
        print("Name:", self.name)
        print("Age:", self.age)


class Student(Person):
    def __init__(self, name, age, roll_no):
        super().__init__(name, age)
        self.roll_no = roll_no

    def display(self):
        print("Student Name:", self.name)
        print("Age:", self.age)
        print("Roll No:", self.roll_no)


class Teacher(Person):
    def __init__(self, name, age, subject):
        super().__init__(name, age)
        self.subject = subject

    def display(self):
        print("Teacher Name:", self.name)
        print("Age:", self.age)
        print("Subject:", self.subject)


people = [
    Student("Gourav", 18, 101),
    Teacher("Vansh", 35, "Python"),
    Student("Jatin", 19, 102)
]

for person in people:
    person.display()
    print()


    #   QUES.  4 _______________

import math

class Shape:
    def area(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius * self.radius


class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width


class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height


shapes = [
    Circle(5),
    Rectangle(10, 4),
    Triangle(8, 6)
]

for shape in shapes:
    print("Area:", round(shape.area(), 2))


     ##    QUES  5 ____________________________________________

class BankAccount:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print("Deposited:", amount)

    def withdraw(self, amount):
        pass

    def show_balance(self):
        print("Balance:", self.balance)


class SavingsAccount(BankAccount):
    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            print("Savings: Withdraw successful")
        else:
            print("Savings: Insufficient balance")


class CurrentAccount(BankAccount):
    def withdraw(self, amount):
        if amount <= self.balance + 5000:
            self.balance -= amount
            print("Current: Withdraw successful")
        else:
            print("Current: Withdrawal limit exceeded")


accounts = [
    SavingsAccount("Gourav", 10000),
    CurrentAccount("Rahul", 5000)
]

for account in accounts:
    account.deposit(1000)
    account.withdraw(7000)
    account.show_balance()


     ###     QUES . 6   =___________________________________


class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def final_price(self):
        return self.price


class Electronics(Product):
    def __init__(self, name, price, warranty):
        super().__init__(name, price)
        self.warranty = warranty

    def final_price(self):
        return self.price + 500


class Clothing(Product):
    def __init__(self, name, price, size):
        super().__init__(name, price)
        self.size = size

    def final_price(self):
        return self.price * 0.90


class Grocery(Product):
    def __init__(self, name, price, weight):
        super().__init__(name, price)
        self.weight = weight

    def final_price(self):
        return self.price * 0.95


products = [
    Electronics("Laptop", 50000, 2),
    Clothing("T-Shirt", 1000, "L"),
    Grocery("Rice", 2000, "10 KG")
]

for product in products:
    print(product.name, "Final Price:", product.final_price())


##     QUES  . 7  ___________________________________

class UniversityMember:
    def __init__(self, name):
        self.name = name

    def activity(self):
        pass


class Student(UniversityMember):
    def activity(self):
        print(self.name, "is attending classes.")


class Professor(UniversityMember):
    def activity(self):
        print(self.name, "is teaching students.")


class Researcher(UniversityMember):
    def activity(self):
        print(self.name, "is doing research.")


members = [
    Student("Gourav"),
    Professor("Dr. Sharma"),
    Researcher("Aman")
]

for member in members:
    member.activity()

    #  QUES  8 _________________________

class Transport:
    def calculate_fare(self, distance):
        pass


class Bus(Transport):
    def calculate_fare(self, distance):
        return distance * 5


class Train(Transport):
    def calculate_fare(self, distance):
        return distance * 3


class Flight(Transport):
    def calculate_fare(self, distance):
        return distance * 10


transports = [
    Bus(),
    Train(),
    Flight()
]

distance = 100

for transport in transports:
    print("Fare for", distance, "km:", transport.calculate_fare(distance))

