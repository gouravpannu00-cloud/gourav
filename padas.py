# import pandas as pd
# marks = pd.Series([90, 85, 78, 92, 88])
# print(marks)

# data = {'Name': ['gourav', 'vansh', 'aman', 'surender', 'poorav'],
#         'Marks': [90, 85, 78, 92, 88]}
# df = pd.DataFrame(data)
# print(df)

# print(df['Name'])
# print(df['Marks'])

# print(df.loc[0])  # Accessing the first row
# print(df.loc[1])  # Accessing the second row

# print(df.loc[0,"Name"])  # Accessing the 'Name' of the first row
# print(df.loc[1,"Marks"])  # Accessing the 'Marks' of the second row

# high_marks = df[df['Marks'] > 80]
# print(high_marks)

# mask = df['Marks'] > 80
# print(mask)

# grouped = df.groupby("Name")["Marks"].mean()
# print(grouped)

# import pandas as pd
# list1 = [5,10,15,20]
# s=pd.Series(list1)
# print(s)

# s=pd.Series((1,2,3,4))
# print(s.loc[1])  

# s=pd.Series({'a':10,'b':20,'c':30})
# print(s.loc['b'])  

# s=pd.Series({'a':10,'b':20,'c':30})
# s.loc['c'] = 35
# print(s)

# list=pd.Series([5,10,15,20,25,30,35,40,45,50])
# print(list[list >= 20])

# s=pd.Series([200,300,400,500],index=['P','Q','R','S'])
# print(s.loc['R'])

# s['R'] += 100
# print(s)

# import pandas as pd
# import numpy as np
# arr = np.array([10,20,30,40,50])
# s = pd.Series(arr)
# print(s.iloc[2])  # Accessing the element at index 2

# import pandas as pd
# s = pd.Series([10, 20, 30, 40, 50])
# print(s[s>20])  # Filtering elements greater than 20

# import pandas as pd
# s = pd.Series([10, 20, 30, 40, 50],
#               index=['A', 'B', 'C', 'D', 'E'])
# s.loc['C'] = 35  # Modifying the value at index 'C'    # UPDATE
# print(s[s>20])  # Filtering elements greater than 20  # FILTER

