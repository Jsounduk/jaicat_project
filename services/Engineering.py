import math

# Define a function to calculate the area of a circle
def calculate_circle_area(radius):
    return math.pi * (radius ** 2)

# Define a function to calculate the volume of a cylinder
def calculate_cylinder_volume(radius, height):
    return math.pi * (radius ** 2) * height

# Define a function to calculate the stress on a beam
def calculate_beam_stress(force, length, width, height):
    return (force * length) / (width * height)

# Define a function to provide engineering calculations to the user
def provide_engineering_calculations():
    print("Engineering Calculations:")
    print("1. Calculate circle area")
    print("2. Calculate cylinder volume")
    print("3. Calculate beam stress")
    choice = input("Enter your choice: ")
    if choice == "1":
        radius = float(input("Enter the radius of the circle: "))
        area = calculate_circle_area(radius)
        print(f"The area of the circle is: {area}")
    elif choice == "2":
        radius = float(input("Enter the radius of the cylinder: "))
        height = float(input("Enter the height of the cylinder: "))
        volume = calculate_cylinder_volume(radius, height)
        print(f"The volume of the cylinder is: {volume}")
    elif choice == "3":
        force = float(input("Enter the force on the beam: "))
        length = float(input("Enter the length of the beam: "))
        width = float(input("Enter the width of the beam: "))
        height = float(input("Enter the height of the beam: "))
        stress = calculate_beam_stress(force, length, width, height)
        print(f"The stress on the beam is: {stress}")
    else:
        print("Invalid choice")

# Example usage:
provide_engineering_calculations()



import wikipedia

# Define a function to search for engineering information on Wikipedia
def search_engineering_topic(topic):
    try:
        page = wikipedia.page(topic)
        return page.content
    except wikipedia.exceptions.DisambiguationError as e:
        return "Disambiguation error: " + str(e)
    except wikipedia.exceptions.PageError:
        return "Page not found"

# Example usage:
topic = "mechanical engineering"
result = search_engineering_topic(topic)
print(result)
