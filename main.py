import pandas as pd
import test
from collections import deque

data = pd.read_csv("./data.csv", delimiter="|")
#index here for the dataFrame (data) which is started with value zero to track all elements in the dataFrame
#iterrow() to move through all rows in the data
data_in_dictionary = {}
for index, row in data.iterrows():
    data_in_dictionary[row['PID']] = test.Data(row['PID'], row['Arrival Time'], row['Priority'],
                                               row['Sequence of CPU and IO bursts'])
    #print(f"{row['PID']}, {row['Arrival Time']}, {row['Priority']}, {row['Sequence of CPU and IO bursts']}")
    print(data_in_dictionary[row['PID']].calculate_total_burst())

new = []
ready = {}
running = []
waiting = []
ter = []
time = 0
running_lock = 0
time_q = 10

new = [i for i in data_in_dictionary.keys()]

test = 0
while True:
    for i in range(len(new)):
        if data_in_dictionary[new[i]].Arrival_Time <= time and data_in_dictionary[new[i]].Check == 0:
            priority = data_in_dictionary[new[i]].Priority
            if priority not in ready.keys():
                ready[priority] = deque()
            ready[priority].append([new[i], data_in_dictionary[new[i]].calculate_total_burst()])
            data_in_dictionary[new[i]].Check = 1


    if len(ready) != 0:
        process = min(ready.keys())
        worker = ready[process].popleft()
        print(worker)
        if worker[1][0][0] == "IO":
            waiting.append([worker[0], worker[1],process, worker[1][0][1] + time])
            worker[1].pop(0)
            if len(ready[process]) == 0:
                ready.pop(process)
        else:
            if worker[1][0][1] <= time_q:
                time = time + worker[1][0][1]
                worker[1][0][1] = 0
                worker[1].pop(0)
                if len(ready[process]) == 0 and len(worker[1]) ==0:
                    ready.pop(process)
                else:
                    ready[process].append(worker)

            else:
                time = time + time_q
                worker[1][0][1] = worker[1][0][1] - time_q
                ready[process].append(worker)
    for i in waiting:
        if i[3] <= time:
            ready[i[2]] = deque()
            ready[i[2]].append([i[0], i[1]])
            waiting.remove(i)
        else:
            time = time + 1
    if len(waiting) == 0 and len(running) == 0 and len(ready) == 0:
        break
