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

