
cars = ["Ford", "Volvo", "BMW", {"car": "Ford", "model": "Mustang", "year": 1964}]

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