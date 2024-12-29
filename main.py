import pandas as pd
import test

data = pd.read_csv("./data.csv", delimiter="|")
#index here for the dataFrame (data) which is started with value zero to track all elements in the dataFrame
#iterrow() to move through all rows in the data
data_in_dictionary = {}
for index,row in data.iterrows():
    data_in_dictionary[row['PID']] = test.Data(row['PID'], row['Arrival Time'], row['Priority'], row['Sequence of CPU and IO bursts'])
    #print(f"{row['PID']}, {row['Arrival Time']}, {row['Priority']}, {row['Sequence of CPU and IO bursts']}")
    print(data_in_dictionary[row['PID']].calculate_total_burst())



