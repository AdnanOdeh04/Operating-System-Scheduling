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
    #print(data_in_dictionary[row['PID']].calculate_total_burst())

new = []
ready = {}
running = []
waiting = []
time = 0
time_q = 10
gantt = []
waiting_time = []
turnaround_time = []
number_process = 0
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
            waiting_time.append([new[i], time - data_in_dictionary[new[i]].Arrival_Time])
            turnaround_time.append([new[i], 0])
            number_process += 1

    if len(ready) != 0:
        process = min(ready.keys())
        worker = ready[process].popleft()

        if worker[1][0][1] <= time_q:
            start_time = time
            time = time + worker[1][0][1]
            gantt.append([start_time, worker[0], time])
            for i in waiting_time:
                if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                    for priority in ready.values():
                        if any(proc[0] == i[0] for proc in priority):
                            i[1] += worker[1][0][1]

            worker[1][0][1] = 0
            worker[1].pop(0)

            if len(worker[1]) > 0:
                if worker[1][0][0] == "IO":
                    waiting.append([worker[0], worker[1], process, worker[1][0][1] + time])
                    worker[1].pop(0)
                    if len(worker[1]) > 0:
                        worker[1] = []

            for i in turnaround_time:
                if i[0] == worker[0]:
                    i[1] = time - data_in_dictionary[worker[0]].Arrival_Time

            if len(ready[process]) == 0 and len(worker[1]) == 0:
                ready.pop(process)

        else:
            start_time = time
            time = time + time_q
            for i in waiting_time:
                if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                    for priority in ready.values():
                        if any(proc[0] == i[0] for proc in priority):
                            i[1] += time_q
            worker[1][0][1] = worker[1][0][1] - time_q
            ready[process].append(worker)
            gantt.append([start_time, worker[0], time])

    for i in waiting:
        if i[3] <= time:
            ready[i[2]] = deque()
            ready[i[2]].append([i[0], i[1]])
            waiting.remove(i)
        else:
            if len(ready) == 0:
                time = time + 1

    if len(waiting) == 0 and len(running) == 0 and len(ready) == 0:
        break

print(gantt)
print(waiting_time)
print(turnaround_time)