import pandas as pd
df = pd.read_csv("C:\\Users\\hp\\Downloads\\customers-100.csv")

print(df)    # first and last 5 rows print hogi

print(df.to_string())  # Display the entire DataFrame as a string

print(df.head())  # Display the first 5 rows of the DataFrame

print(df.tail())  # Display the last 5 rows of the DataFrame

print(df.info())  # Display information about the DataFrame, including column names, data types, and non-null counts

print(df.describe())  # Display summary statistics for numerical columns in the DataFrame