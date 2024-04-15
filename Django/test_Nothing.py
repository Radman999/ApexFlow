cars = ["Ford", "Volvo", "BMW", {"car": "Ford", "model": "Mustang", "year": 1964}]

#create a list that contains objects of different types
cars = ["Ford", "Volvo", "BMW", {"car": "Ford", "model": "Mustang", "year": 1964},]

# print the objects inside the cars
if isinstance(cars[-1], dict):
    for key, value in cars[-1].items():
        print(key, value)

print(cars[-1])

# printh the objects inside the cars list
for car in cars:
    if isinstance(car, dict):
        for key, value in car.items():
            print(key, value)

# BEGIN: Test Cases
# Test case 1: Additional list with objects
cars2 = ["Toyota", "Honda", "Mercedes", {"car": "Toyota", "model": "Camry", "year": 2020}]

# Test case 2: Empty list
cars3 = []

# Test case 3: List with only strings
cars4 = ["Audi", "Lamborghini", "Ferrari"]

# Test case 4: List with only dictionaries
cars5 = [{"car": "Chevrolet", "model": "Camaro", "year": 2019}, {"car": "Tesla", "model": "Model S", "year": 2022}]

# Test case 5: List with mixed types
cars6 = ["Nissan", {"car": "Mazda", "model": "CX-5", "year": 2018}, "Subaru", {"car": "Jeep", "model": "Wrangler", "year": 2021}]

# END: Test Casescars = ["Ford", "Volvo", "BMW", {"car": "Ford", "model": "Mustang", "year": 1964}]

#create a list that contains objects of different types
cars = ["Ford", "Volvo", "BMW", {"car": "Ford", "model": "Mustang", "year": 1964},]


    # print the objects inside the cars
# if isinstance(cars[-1], dict):
#     for key, value in cars[-1].items():
#          print(key, value)

# print(cars[-1])


# printh the objects inside the cars list

for car in cars:
    if isinstance(car, dict):
        for key, value in car.items():
            print(key, value)


# BEGIN: Test Cases
# Test case 1: Additional list with objects
cars2 = ["Toyota", "Honda", "Mercedes", {"car": "Toyota", "model": "Camry", "year": 2020}]
for car in cars2:
    if isinstance(car, dict):
        for key, value in car.items():
            print(key, value)

# Test case 2: Empty list
cars3 = []
for car in cars3:
    if isinstance(car, dict):
        for key, value in car.items():
            print(key, value)

# Test case 3: List with only strings
cars4 = ["Audi", "Lamborghini", "Ferrari"]
for car in cars4:
    if isinstance(car, dict):
        for key, value in car.items():
            print(key, value)

# Test case 4: List with only dictionaries
cars5 = [{"car": "Chevrolet", "model": "Camaro", "year": 2019}, {"car": "Tesla", "model": "Model S", "year": 2022}]
for car in cars5:
    if isinstance(car, dict):
        for key, value in car.items():
            print(key, value)

# Test case 5: List with mixed types
cars6 = ["Nissan", {"car": "Mazda", "model": "CX-5", "year": 2018}, "Subaru", {"car": "Jeep", "model": "Wrangler", "year": 2021}]
for car in cars6:
    if isinstance(car, dict):
        for key, value in car.items():
            print(key, value)
# END: Test Cases