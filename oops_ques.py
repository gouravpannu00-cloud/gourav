      #   QUES.  1 _______________________

from os import name


from unicodedata import name


class student:
    def __init__(self,name,age,marks):
        self.name = name
        self.age = age
        self.marks = marks

s1 = student("Gourav",19,99)
print("Student Name:", s1.name)
print("Student Age:", s1.age)
print("Student Marks:", s1.marks)


    #    QUES.   2 ______________________________
class car:
    def __init__(self,brand,model):
        self.brand = brand
        self.model = model

car1 = car("toyota","Fortuner")
car2 = car("honda","city")
print("Car1 :", car1.brand, car1.model)
print("Car2:", car2.brand, car2.model)

     #   QUES.  3 _____________________________

class rectangle:
    def __init__(self,length,width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width

r1 = rectangle(10, 5)
print("Area of rectangle:", r1.area())


   #   QUES.  4 _____________________________

class animal:
    def sound(self):
        return "Animal makes a sound"

class dog(animal):
    def sound(self):
        return "Dog barks"

dog1 = dog()
print(dog1.sound())


    #    QUES.  5 _____________________________
class person:
    def __init__(self,name,age):
        self.name = name
        self.age = age

    def display(self):
        print("Name:", self.name)
        print("Age:", self.age)

p1 = person("Gourav", 25)
p2 = person("Jatin", 30)

p1.display()
p2.display()