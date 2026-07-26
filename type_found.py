a = 10
b = 10.5
c = "Hello"
d = True
e = [1, 2, 3]

print(type(a))  # <class 'int'>
print(type(b))  # <class 'float'>
print(type(c))  # <class 'str'>
print(type(d))  # <class 'bool'>
print(type(e))  # <class 'list'>

   #   found largest number 


a = int(input("Enter first number: "))
b = int(input("Enter second number: "))

if a > b:
    print("Largest =", a)
else:
    print("Largest =", b)