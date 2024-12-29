import pandas as pd

data = pd.read_csv("./data.csv", delimiter="|")
#index here for the dataFrame (data) which is started with value zero to track all elements in the dataFrame
#iterrow() to move through all rows in the data
for index,row in data.iterrows():
    print(f"{row['PID']}, {row['Arrival Time']}, {row['Priority']}, {row['Sequence of CPU and IO bursts']}")



