       #   RIGHT   TRIANGLE ________________________________________________________
# for i in range(1,6):
#     for j in range (i):
#         print ("*" , end = "  " )
#     print()

        #    RIGHT    TRIANGLE _______________________________________________

# rows = 5

# for i in range (1 , rows + 1 ):
#     print(" * " * i )

            #   INVERTED    RIGHT    TRIANGLE     .....................................

# rows = 5
# for i in range (rows , 0,-1):
#     print(" * " * i)

           #     NUMBER     TRIANGLE   ..........................................

# rows = 5 
# for i in range (1,rows +1):
#     for j in range (1 , i + 1 ):
#         print (j , end = " ")
#     print()

           #    NESTED  LOOP   FORMAYT  .............................................

# for i in range (1,6):
#     for j in range ( i ):
#         print ( i , end = " ")
#     print ()

           #        SQUARE ...................................

# rows = 5
# for i in range (1, rows+1):
#     for j in range (1 , rows+1):
#         print ( " * " , end = " ")
#     print()

         #    HOLLOW      SQUARE ________________________________________________________

for i in range (5):
    for j in range (5):
        if i == 0 or i == 4 or j == 0 or j == 4 :
            print("*", end = " ")
        else :
            print(" ", end = " ")
    print()