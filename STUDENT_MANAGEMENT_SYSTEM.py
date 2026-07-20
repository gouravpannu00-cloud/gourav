# Student Management System

students = []

while True:
    print("\n===== Student Management System =====")
    print("1. Add Student")
    print("2. View All Students")
    print("3. Search Student")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Exit")

    choice = input("Enter Choice: ")

    # Add Student
    if choice == "1":
        sid = input("Enter Student ID: ")
        name = input("Enter Name: ")
        age = input("Enter Age: ")
        course = input("Enter Course: ")

        student = [sid, name, age, course]
        students.append(student)

        print("Student Added Successfully!")

    # View All Students
    elif choice == "2":
        if len(students) == 0:
            print("No Students Found!")
        else:
            for student in students:
                print("------------------------")
                print("ID:", student[0])
                print("Name:", student[1])
                print("Age:", student[2])
                print("Course:", student[3])
            print("------------------------")

    # Search Student
    elif choice == "3":
        sid = input("Enter Student ID: ")
        found = False

        for student in students:
            if student[0] == sid:
                print("------------------------")
                print("ID:", student[0])
                print("Name:", student[1])
                print("Age:", student[2])
                print("Course:", student[3])
                print("------------------------")
                found = True
                break

        if not found:
            print("Student Not Found!")

    # Update Student
    elif choice == "4":
        sid = input("Enter Student ID: ")
        found = False

        for student in students:
            if student[0] == sid:
                student[1] = input("Enter New Name: ")
                student[2] = input("Enter New Age: ")
                student[3] = input("Enter New Course: ")
                print("Student Updated Successfully!")
                found = True
                break

        if not found:
            print("Student Not Found!")

    # Delete Student
    elif choice == "5":
        sid = input("Enter Student ID: ")
        found = False

        for student in students:
            if student[0] == sid:
                students.remove(student)
                print("Student Deleted Successfully!")
                found = True
                break

        if not found:
            print("Student Not Found!")

    # Exit
    elif choice == "6":
        print("Thank You!")
        break

    # Invalid Choice
    else:
        print("Invalid Choice! Please try again.")