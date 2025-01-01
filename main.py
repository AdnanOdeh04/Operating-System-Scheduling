import pandas as pd
import test
from collections import deque
import re

data = pd.read_csv("./data.csv", delimiter="|")
#index here for the dataFrame (data) which is started with value zero to track all elements in the dataFrame
#iterrow() to move through all rows in the data
data_in_dictionary = {}
for index, row in data.iterrows():
    data_in_dictionary[row['PID']] = test.Data(row['PID'], row['Arrival Time'], row['Priority'],
                                               row['Sequence of CPU and IO bursts'])
    #print(f"{row['PID']}, {row['Arrival Time']}, {row['Priority']}, {row['Sequence of CPU and IO bursts']}")
    #print(data_in_dictionary[row['PID']].calculate_total_burst())

graph_processes = {}    #{"PID":[processes or resources]} all p or r in the list are connected directly to the process PID
assigned_list = []
ready = {}
ready_res = {}
running = []
waiting = []
time = 0
time_q = 10
gantt = []
waiting_time = []
turnaround_time = []
number_process = 0
new = [i for i in data_in_dictionary.keys()]
rosources_list = []
resource_busy=0
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
        resource_busy = 0
        process = min(ready.keys())
        worker = ready[process].popleft()
        #Here when a new process comes insert it to the graph
        if worker[0] not in graph_processes.keys():
            graph_processes[str(worker[0])] = []
        testRequestFirst = re.search(r"R\[[0-9]*\]",str(worker[1][0][1][0]))
        testFreeFirst = re.search(r"F\[[0-9]*\]", str(worker[1][0][1][0]))
        if str(worker[1][0][1][0]).isdigit():
            if int(worker[1][0][1][0]) <= time_q:
                start_time = time
                time = time + int(worker[1][0][1][0])
                for i in waiting_time:
                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                        for priority in ready.values():
                            if any(proc[0] == i[0] for proc in priority):
                                i[1] += int(worker[1][0][1][0])
                #left val
                left_value = time_q - worker[1][0][1][0]
                worker[1][0][1][0] = 0
                worker[1][0][1].pop(0)
                if len(worker[1][0][1]) == 0:
                    worker[1].pop(0)
                else:
                    while True:
                        testRequest = re.search(r"R\[[0-9]*\]",worker[1][0][1][0])
                        testFree = re.search(r"F\[[0-9]*\]", worker[1][0][1][0])
                        if testRequest:
                            #make the Request
                            if worker[1][0][1][0] not in assigned_list:
                                graph_processes[str(worker[1][0][1][0])] = []
                                graph_processes[str(worker[1][0][1][0])].append(str(worker[0]))
                                assigned_list.append(str(worker[1][0][1][0]))
                                worker[1][0][1].pop(0)
                            else:
                                graph_processes[str(worker[0])].append(str(worker[1][0][1][0]))
                                ready_res[process].append([worker[0],worker[1]])
                                resource_busy = 1
                                break

                            if len(worker[1][0][1]) == 0:
                                worker[1].pop(0)
                                break
                            if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                break
                            elif left_value > 0 and len(worker[1][0][1]) > 0:
                                if str(worker[1][0][1][0]).isdigit():
                                    if int(worker[1][0][1][0]) <= left_value:
                                        time = time+worker[1][0][1][0]
                                        left_value = left_value-worker[1][0][1][0]
                                        worker[1][0][1].pop(0)
                                        if len(worker[1][0][1]) == 0:
                                            worker[1].pop(0)
                                        if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                            break
                                    else:
                                        time = time+left_value
                                        worker[1][0][1][0] = worker[1][0][1][0]-left_value
                                        left_value = 0
                                        break
                        elif testFree:
                            #make the free
                            #to search whether the resources to be freed is already allocated or not
                            Form_resource_to_be_freed = "R[" + worker[1][0][1][0][2] + "]"
                            if Form_resource_to_be_freed in assigned_list:
                                #remove the resource from the graph
                                del graph_processes[str(Form_resource_to_be_freed)]
                                assigned_list.remove(Form_resource_to_be_freed)
                            else:
                                print("Free for a resource not exit!")
                                exit(0)
                            worker[1][0][1].pop(0)
                            if len(worker[1][0][1]) == 0:
                                worker[1].pop(0)
                                break
                            if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                break
                            elif left_value > 0 and len(worker[1][0][1]) > 0:
                                if str(worker[1][0][1][0]).isdigit():
                                    if int(worker[1][0][1][0]) <= left_value:
                                        time = time+worker[1][0][1][0]
                                        left_value = left_value-worker[1][0][1][0]
                                        worker[1][0][1].pop(0)
                                        if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                            break
                                    else:
                                        time = time+left_value
                                        worker[1][0][1][0] = worker[1][0][1][0]-left_value
                                        left_value = 0
                                        break
                        else:
                            print("Error in the File")
                            exit()
                if resource_busy == 1:
                    continue
                gantt.append([start_time, worker[0], time])
                if len(worker[1]) > 0:
                    if worker[1][0][0] == "IO":
                        waiting.append([worker[0], worker[1], process, int(worker[1][0][1][0]) + time])
                        worker[1].pop(0)
                        if len(worker[1][0][1]) == 0:
                            worker[1].pop(0)
                        if len(worker[1]) > 0:
                            worker[1] = []
                    else:
                        ready[process].append(worker)
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
                worker[1][0][1][0] = int(worker[1][0][1][0]) - time_q
                ready[process].append(worker)
                gantt.append([start_time, worker[0], time])


        elif testRequestFirst or testFreeFirst:
            #make the Request
            #here we call a function for an allocation for the allocation of the Graoh (For DeadLock Detection)
            if testRequestFirst:
                if str(worker[1][0][1][0]) not in assigned_list:
                    graph_processes[str(worker[1][0][1][0])] = []
                    graph_processes[str(worker[1][0][1][0])].append(str(worker[0]))
                    assigned_list.append(str(worker[1][0][1][0]))
                else:
                    graph_processes[str(worker[0])].append(str(worker[1][0][1][0]))
                    ready_res[process].append([worker[0], worker[1]])
                    continue
            elif testFreeFirst:
                Form_resource_to_be_freed = "R[" + worker[1][0][1][0][2] + "]"
                if Form_resource_to_be_freed in assigned_list:
                    # remove the resource from the graph
                    del graph_processes[str(Form_resource_to_be_freed)]
                    assigned_list.remove(Form_resource_to_be_freed)
                else:
                    print("Free for a resource not exit!")
                    exit(0)
            worker[1][0][1].pop(0)
            start_time=time
            if len(worker[1][0][1]) == 0:
                worker[1].pop(0)
                break
            while True:
                left_value = time_q
                testRequest = re.search(r"R\[[0-9]*\]",str(worker[1][0][1][0]))
                testFree = re.search(r"F\[[0-9]*\]", str(worker[1][0][1][0]))
                if testRequest:
                    #make the Request
                    worker[1][0][1].pop(0)
                    if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                        break
                    elif left_value > 0 and len(worker[1][0][1]) > 0:
                        if str(worker[1][0][1][0]).isdigit():
                            if int(worker[1][0][1][0]) <= left_value:
                                time = time+worker[1][0][1][0]
                                left_value = left_value-worker[1][0][1][0]
                                worker[1][0][1].pop(0)
                                if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                    break
                            else:
                                time = time+left_value
                                worker[1][0][1][0] = worker[1][0][1][0]-left_value
                                left_value = 0
                                break
                elif testFree:
                    #make the free
                    worker[1][0][1].pop(0)
                    if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                        break
                    elif left_value > 0 and len(worker[1][0][1]) > 0:
                        if str(worker[1][0][1][0]).isdigit():
                            if int(worker[1][0][1][0]) <= left_value:
                                time = time+worker[1][0][1][0]
                                left_value = left_value-worker[1][0][1][0]
                                worker[1][0][1].pop(0)
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += worker[1][0][1][0]
                                if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                    break
                            else:
                                time = time+left_value
                                worker[1][0][1][0] = worker[1][0][1][0]-left_value
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += left_value
                                left_value = 0
                                break
                else:
                    if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                        break
                    elif left_value > 0 and len(worker[1][0][1]) > 0:
                        if str(worker[1][0][1][0]).isdigit():
                            if int(worker[1][0][1][0]) <= left_value:
                                time = time+worker[1][0][1][0]
                                left_value = left_value-worker[1][0][1][0]
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += worker[1][0][1][0]

                                worker[1][0][1].pop(0)
                                if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                    break
                            else:
                                time = time+left_value
                                worker[1][0][1][0] = worker[1][0][1][0]-left_value
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += left_value
                                left_value = 0
                                break

            gantt.append([start_time, worker[0], time])
            ready[process].append(worker)

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
print(graph_processes)