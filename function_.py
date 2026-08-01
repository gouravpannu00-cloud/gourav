def cal_sum (a,b):
    sum = a + b
    print(sum)
    return sum

cal_sum(5, 10)
cal_sum(20, 30)


def check_even_odd(num):
    if num % 2 == 0:
        print("this  is even")
    else:
        print("this is odd")

check_even_odd(5)
check_even_odd(10)


              #   CONVERT    USD   TO    INR  ___________________________--
def converter (usd):
    inr = usd * 82.74
    print(inr)
converter(100)
converter(200)


cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
def print_cities(cities):
    for city in cities:
        print(city)
print_cities(cities)


def calculate_factorial(n):
    fact = 1
    for i in range(1, n + 1):
        fact *= i
    print(fact)
calculate_factorial(5)
calculate_factorial(7)
calculate_factorial(10)