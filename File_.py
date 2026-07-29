# # with open ("practice.txt","w") as f:
# #     f.write("hii everyone \n we are learning file input and output \n ")
# #     f.write("using java. \n i like programing in java .")


# with open("practice.txt","r")as f:
#     data=f.read()

# new_data = data.replace("java","python")
# print(new_data)    

# with open("practice.txt","w") as f:
#     f.write (new_data)


import os
open("student.txt","w")

f=open ("student.txt","w")
print(f.write("Name:John"))
f.close()

f=open("student.txt","r")
print(f.read())
f.close()

x=open("student.txt","a")
x.write(" \ncity:Delhi")