class BankAccount:
    def __init__(self, account_holder, balance):
        self.account_holder = account_holder
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print("Deposited:", amount)

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            print("Withdrawn:", amount)
        else:
            print("Insufficient balance")

    def display(self):
        print("Account Holder:", self.account_holder)
        print("Balance:", self.balance)


account = BankAccount("Gourav", 10000)

account.deposit(2000)
account.withdraw(3000)

account.display()




class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary


class Manager(Employee):
    def __init__(self, name, salary, department):
        super().__init__(name, salary)
        self.department = department


manager = Manager("Gourav", 50000, "IT")

print("Name:", manager.name)
print("Salary:", manager.salary)
print("Department:", manager.department)


class Vehicle:
    def start(self):
        print("Vehicle is starting")


class Car(Vehicle):
    def start(self):
        print("Car starts with a key")


class Bike(Vehicle):
    def start(self):
        print("Bike starts with a self-start button")


car = Car()
bike = Bike()

vehicles = [car, bike]

for vehicle in vehicles:
    vehicle.start()


class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def calculate_grade(self):
        if self.marks >= 80:
            return "A"
        elif self.marks >= 60:
            return "B"
        elif self.marks >= 50:
            return "C"
        elif self.marks >= 40:
            return "D"
        else:
            return "F"


student1 = Student("Gourav", 85)
student2 = Student("Rahul", 65)
student3 = Student("Aman", 35)

students = [student1, student2, student3]

for student in students:
    print(student.name, "Grade:", student.calculate_grade())


class Shape:
    def area(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius * self.radius


class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width


circle = Circle(5)
rectangle = Rectangle(10, 5)

shapes = [circle, rectangle]

for shape in shapes:
    print("Area:", shape.area())

class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def total_price(self):
        return self.price * self.quantity


product1 = Product("Laptop", 50000, 1)
product2 = Product("Mouse", 500, 2)
product3 = Product("Keyboard", 1000, 3)

products = [product1, product2, product3]

for product in products:
    print(product.name, "Total Price:", product.total_price())


class Animal:
    def __init__(self, name):
        self.name = name


class Dog(Animal):
    def sound(self):
        print(self.name, "says Woof")


class Cat(Animal):
    def sound(self):
        print(self.name, "says Meow")


dog = Dog("Tommy")
cat = Cat("Kitty")

animals = [dog, cat]

for animal in animals:
    animal.sound()