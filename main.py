
import matplotlib.pyplot as plt
import pandas as pd
import test
from collections import deque
import re

data = pd.read_csv("./data.csv", delimiter="|")
# index here for the dataFrame (data) which is started with value zero to track all elements in the dataFrame
# iterrow() to move through all rows in the data
data_in_dictionary = {}
for index, row in data.iterrows():
    data_in_dictionary[row['PID']] = test.Data(row['PID'], row['Arrival Time'], row['Priority'],
                                               row['Sequence of CPU and IO bursts'])
    # print(f"{row['PID']}, {row['Arrival Time']}, {row['Priority']}, {row['Sequence of CPU and IO bursts']}")
    # print(data_in_dictionary[row['PID']].calculate_total_burst())

graph_processes = {}  # {"PID":[processes or resources]} all p or r in the list are connected directly to the process PID
assigned_list = []
ready = {}
waiting_res = {}
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
resource_busy = 0
finish_recovery = 0
process_handle_deadlock = []
terminated_processes_list = {}


######################################################################################################################################
def calc_turnaroundtTime(dict, turnTime, gant):
    endTime = 0
    for T in turnTime:
        c = len(gant) - 1

        while c >= 0:
            if int(T[0]) == int(gant[c][1]):
                endTime = int(gant[c][2])
                break
            c -= 1
        arrivalTime = int(dict[int(T[0])].Arrival_Time)
        T[1] = endTime - arrivalTime


def calc_average_watingTime(waitingTime, number_process):
    process_waiting_time = [p[1] for p in waitingTime]
    average_waitingTime = sum(process_waiting_time) / number_process
    average_waitingTime = round(average_waitingTime, 2)
    print("the waiting time for every process is: ", waitingTime)
    print("the average waiting time is: ", average_waitingTime)


# ################################################ dead Lock Detection part ##########################################################
def deadLockDetection(graph, TargetedProcess, data_dict,
                      process_in_deadLock):
    listProcesses = []
    list_processes_inDeadLock = {}
    for vertex in graph.keys():
        deadlocked_processes = []
        testProcess = re.search(r"^[0-9]*$", str(vertex))
        if testProcess and vertex not in listProcesses:
            listProcesses.append(str(vertex))
        pointer = graph[vertex]
        while pointer in graph.keys() and graph[pointer] not in listProcesses:
            if pointer not in listProcesses and re.search(r"^[0-9]*$", str(pointer)):
                listProcesses.append(pointer)
                deadlocked_processes.append(pointer)
            pointer = graph[pointer]
        if pointer in graph.keys():
            process_in_deadLock.append(deadlocked_processes)
            if graph[pointer] in listProcesses:
                for process in deadlocked_processes:
                    priority = data_dict[int(process)].Priority
                    list_processes_inDeadLock[priority] = process
                TargetedProcess.append(list_processes_inDeadLock[max(list_processes_inDeadLock.keys())])
                return True
        else:
            continue
    return False


# #######################################################################################################################################
# ################################################ dead Lock recovery part #############################################################
def recovery(graph_processes, waiting_res, assigned_list, process_to_handle_deadlock, finished_recovery,
             data_in_dictionary, terminated_process_list):
    # print(graph_processes)
    process_in_deadLock = []
    while deadLockDetection(graph_processes, process_to_handle_deadlock, data_in_dictionary, process_in_deadLock):
        List_resource_tobedeleted = []
        delete_requested = []
        if graph_processes[str(process_to_handle_deadlock[0])] in waiting_res.keys():
            # print(waiting_res[graph_processes[str(process_to_handle_deadlock[0])]])
            del waiting_res[graph_processes[str(process_to_handle_deadlock[0])]]
        for vertices in graph_processes:
            if graph_processes[vertices] == str(process_to_handle_deadlock[0]):
                List_resource_tobedeleted.append(vertices)
                if str(vertices) in assigned_list:
                    assigned_list.remove(vertices)
        # print(List_resource_tobedeleted)
        while List_resource_tobedeleted:
            del graph_processes[List_resource_tobedeleted[0]]
            for vertices in graph_processes:
                if graph_processes[vertices] == str(List_resource_tobedeleted[0]):
                    delete_requested.append(vertices)
            List_resource_tobedeleted.pop(0)
        if graph_processes[str(process_to_handle_deadlock[0])] in graph_processes.keys():
            # print(graph_processes[str(process_to_handle_deadlock[0])])
            del graph_processes[str(process_to_handle_deadlock[0])]
        if str(process_to_handle_deadlock[0]) in assigned_list:
            # print(str(process_to_handle_deadlock[0]))
            assigned_list.remove(str(process_to_handle_deadlock[0]))
        while delete_requested:
            del graph_processes[delete_requested[0]]
            delete_requested.pop(0)
        # when the process is terminated add it to the ready queue to start from the begining

        for process in data_in_dictionary.keys():
            if str(process) == str(process_to_handle_deadlock[0]):
                priority = data_in_dictionary[process].Priority
                if priority not in terminated_process_list.keys():
                    terminated_process_list[priority] = deque()
                terminated_process_list[priority].append([process, data_in_dictionary[process].calculate_total_burst()])
                break
    finished_recovery[0] = 1


# #######################################################################################################################################

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
while True:
    process_handle_deadlock = []
    finish_recovery = []
    finish_recovery.append(0)
    for process_R in waiting_res.keys():
        if process_R not in assigned_list:
            if waiting_res[process_R][0][0] not in ready.keys():
                ready[waiting_res[process_R][0][0]] = deque()
                ready[waiting_res[process_R][0][0]].append([waiting_res[process_R][0][1], waiting_res[process_R][0][2]])
            else:
                ready[waiting_res[process_R][0][0]].append([waiting_res[process_R][0][1], waiting_res[process_R][0][2]])
            if len(waiting_res[process_R]) > 1:
                waiting_res[process_R].popleft()
            else:
                waiting_res.pop(process_R)
                break
    if len(terminated_processes_list.keys()) > 0:
        for process_T in terminated_processes_list.keys():
            priority = data_in_dictionary[terminated_processes_list[process_T][0][0]].Priority
            if priority not in ready.keys():
                ready[priority] = deque()
            ready[priority].append(
                [terminated_processes_list[priority][0][0], terminated_processes_list[priority][0][1]])
            del terminated_processes_list[priority]
            break

    process_in_deadLock = []
    resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                       process_in_deadLock)
    if resultDeadLock:
        print("HandleDeadLockHere1")
        List_resource_tobedeleted = []
        recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock, finish_recovery,
                 data_in_dictionary, terminated_processes_list)
        if finish_recovery[0] == 1:
            print(
                f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
            process_in_deadLock = []
            continue
    if len(ready) != 0:
        resource_busy = 0
        process = min(ready.keys())
        worker = ready[process].popleft()
        if len(worker[1][0][1]) == 0:
            break
        # Here when a new process comes insert it to the graph
        testRequestFirst = re.search(r"R\[[0-9]*\]", str(worker[1][0][1][0]))
        testFreeFirst = re.search(r"F\[[0-9]*\]", str(worker[1][0][1][0]))
        # ########################## start ################################
        if str(worker[1][0][1][0]).isdigit():
            if int(worker[1][0][1][0]) <= time_q:
                start_time = time
                time = time + int(worker[1][0][1][0])
                for i in waiting_time:
                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                        for priority in ready.values():
                            if any(proc[0] == i[0] for proc in priority):
                                i[1] += int(worker[1][0][1][0])
                # left val
                left_value = time_q - worker[1][0][1][0]
                worker[1][0][1][0] = 0
                worker[1][0][1].pop(0)
                if len(worker[1][0][1]) == 0:
                    worker[1].pop(0)
                else:
                    while True:
                        if len(worker[1][0][1]) == 0:
                            break
                        testRequest = re.search(r"R\[[0-9]*\]", worker[1][0][1][0])
                        testFree = re.search(r"F\[[0-9]*\]", worker[1][0][1][0])
                        if testRequest:
                            # make the Request
                            if worker[1][0][1][0] not in assigned_list:
                                graph_processes[str(worker[1][0][1][0])] = str(worker[0])
                                assigned_list.append(str(worker[1][0][1][0]))
                                worker[1][0][1].pop(0)
                                process_in_deadLock = []
                                resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock,
                                                                   data_in_dictionary, process_in_deadLock)
                                if resultDeadLock:
                                    print("HandleDeadLockHere1")
                                    List_resource_tobedeleted = []
                                    recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                             finish_recovery, data_in_dictionary, terminated_processes_list)
                                    if finish_recovery[0] == 1:
                                        print(
                                            f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                        process_in_deadLock = []
                                        break
                            else:
                                resource_busy = 1
                                graph_processes[str(worker[0])] = str(worker[1][0][1][0])
                                waiting_res[worker[1][0][1][0]] = deque()
                                waiting_res[worker[1][0][1][0]].append([process, worker[0], worker[1]])
                                process_in_deadLock = []
                                resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock,
                                                                   data_in_dictionary, process_in_deadLock)
                                if resultDeadLock:
                                    print("HandleDeadLockHere1")
                                    List_resource_tobedeleted = []
                                    recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                             finish_recovery, data_in_dictionary, terminated_processes_list)
                                    if finish_recovery[0] == 1:
                                        worker[1] = []
                                        print(
                                            f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                        process_in_deadLock = []
                                        break
                                if len(ready[process]) == 0:
                                    ready.pop(process)

                                break
                            if len(worker[1][0][1]) == 0:
                                worker[1].pop(0)
                                break
                            if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                break
                            elif left_value > 0 and len(worker[1][0][1]) > 0:
                                if str(worker[1][0][1][0]).isdigit():
                                    if int(worker[1][0][1][0]) <= left_value:
                                        time = time + worker[1][0][1][0]
                                        left_value = left_value - worker[1][0][1][0]
                                        worker[1][0][1].pop(0)
                                        if len(worker[1][0][1]) == 0:
                                            worker[1].pop(0)
                                        if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                            break
                                    else:
                                        time = time + left_value
                                        worker[1][0][1][0] = worker[1][0][1][0] - left_value
                                        left_value = 0
                                        break
                        elif testFree:
                            # make the free
                            # to search whether the resources to be freed is already allocated or not
                            Form_resource_to_be_freed = "R[" + worker[1][0][1][0][2] + "]"
                            if Form_resource_to_be_freed in assigned_list:
                                # remove the resource from the graph
                                del graph_processes[str(Form_resource_to_be_freed)]
                                assigned_list.remove(Form_resource_to_be_freed)
                                for vertex in graph_processes:
                                    testProcess = re.search(r"^[0-9]*$", str(vertex))
                                    if testProcess:
                                        if graph_processes[vertex] not in assigned_list:
                                            del graph_processes[vertex]
                                            break
                                process_in_deadLock = []
                                resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock,
                                                                   data_in_dictionary, process_in_deadLock)
                                if resultDeadLock:
                                    print("HandleDeadLockHere1")
                                    List_resource_tobedeleted = []
                                    recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                             finish_recovery, data_in_dictionary, terminated_processes_list)
                                    if finish_recovery[0] == 1:
                                        worker[1] = []
                                        print(
                                            f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                        process_in_deadLock = []
                                        break
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
                                        time = time + worker[1][0][1][0]
                                        left_value = left_value - worker[1][0][1][0]
                                        worker[1][0][1].pop(0)
                                        if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                            break
                                    else:
                                        time = time + left_value
                                        worker[1][0][1][0] = worker[1][0][1][0] - left_value
                                        left_value = 0
                                        break
                        else:
                            print("Error in the File")
                            exit()
                if resource_busy == 1:
                    gantt.append([start_time, worker[0], time])
                    continue
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
                gantt.append([start_time, worker[0], time])

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

        ######################################################################################################################################################################################################
        elif testRequestFirst or testFreeFirst:
            # make the Request
            # here we call a function for an allocation for the allocation of the Graoh (For DeadLock Detection)
            if testRequestFirst:
                if str(worker[1][0][1][0]) not in assigned_list:
                    graph_processes[str(worker[1][0][1][0])] = str(worker[0])
                    assigned_list.append(str(worker[1][0][1][0]))
                    process_in_deadLock = []
                    resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                                       process_in_deadLock)
                    if resultDeadLock:
                        print("HandleDeadLockHere1")
                        List_resource_tobedeleted = []
                        recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock, finish_recovery,
                                 data_in_dictionary, terminated_processes_list)
                        if finish_recovery[0] == 1:
                            print(
                                f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                            process_in_deadLock = []
                            continue
                else:
                    graph_processes[str(worker[0])] = (worker[1][0][1][0])
                    waiting_res[worker[1][0][1][0]] = deque()
                    waiting_res[worker[1][0][1][0]].append([process, worker[0], worker[1]])
                    process_in_deadLock = []
                    resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                                       process_in_deadLock)
                    if resultDeadLock:
                        print("HandleDeadLockHere1")
                        List_resource_tobedeleted = []
                        recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock, finish_recovery,
                                 data_in_dictionary, terminated_processes_list)
                        if finish_recovery[0] == 1:
                            print(
                                f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                            process_in_deadLock = []
                            continue
                    continue
            elif testFreeFirst:
                Form_resource_to_be_freed = "R[" + worker[1][0][1][0][2] + "]"
                if Form_resource_to_be_freed in assigned_list:
                    # remove the resource from the graph
                    del graph_processes[str(Form_resource_to_be_freed)]
                    assigned_list.remove(Form_resource_to_be_freed)
                    for vertex in graph_processes:
                        testProcess = re.search(r"^[0-9]*$", str(vertex))
                        if testProcess:
                            if graph_processes[vertex] not in assigned_list:
                                del graph_processes[vertex]
                                break
                    process_in_deadLock = []
                    resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                                       process_in_deadLock)
                    if resultDeadLock:
                        print("HandleDeadLockHere1")
                        List_resource_tobedeleted = []
                        recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock, finish_recovery,
                                 data_in_dictionary, terminated_processes_list)
                        if finish_recovery[0] == 1:
                            print(
                                f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                            process_in_deadLock = []
                            continue
                else:
                    print("Free for a resource not exit!")
                    exit(0)
            worker[1][0][1].pop(0)
            start_time = time
            if len(worker[1][0][1]) == 0:
                worker[1].pop(0)
                break
            while True:
                ########################################################################
                if len(worker[1][0][1]) == 0:
                    break
                left_value = time_q
                testRequest = re.search(r"R\[[0-9]*\]", str(worker[1][0][1][0]))
                testFree = re.search(r"F\[[0-9]*\]", str(worker[1][0][1][0]))
                if testRequest:
                    # if the next value is Request a rosourc
                    # make the Request
                    if str(worker[1][0][1][0]) not in assigned_list:
                        graph_processes[str(worker[1][0][1][0])] = str(worker[0])
                        assigned_list.append(str(worker[1][0][1][0]))
                        process_in_deadLock = []
                        resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                                           process_in_deadLock)
                        if resultDeadLock:
                            print("HandleDeadLockHere1")
                            List_resource_tobedeleted = []
                            recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                     finish_recovery, data_in_dictionary, terminated_processes_list)
                            if finish_recovery[0] == 1:
                                print(
                                    f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                process_in_deadLock = []
                                break
                    else:
                        graph_processes[str(worker[0])] = (worker[1][0][1][0])
                        waiting_res[worker[1][0][1][0]] = deque()
                        waiting_res[worker[1][0][1][0]].append([process, worker[0], worker[1]])
                        process_in_deadLock = []
                        resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                                           process_in_deadLock)
                        if resultDeadLock:
                            print("HandleDeadLockHere1")
                            List_resource_tobedeleted = []
                            recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                     finish_recovery, data_in_dictionary, terminated_processes_list)
                            if finish_recovery[0] == 1:
                                worker = []
                                print(
                                    f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                process_in_deadLock = []
                                break
                        break
                    worker[1][0][1].pop(0)
                    if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                        break
                    elif left_value > 0 and len(worker[1][0][1]) > 0:
                        if str(worker[1][0][1][0]).isdigit():
                            if int(worker[1][0][1][0]) <= left_value:
                                time = time + worker[1][0][1][0]
                                left_value = left_value - worker[1][0][1][0]
                                worker[1][0][1].pop(0)
                                if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                    break
                            else:
                                time = time + left_value
                                worker[1][0][1][0] = worker[1][0][1][0] - left_value
                                left_value = 0
                                break
                #########################################################################
                elif testFree:
                    # if the next value is free a rosource
                    # make the free
                    Form_resource_to_be_freed = "R[" + worker[1][0][1][0][2] + "]"
                    if Form_resource_to_be_freed in assigned_list:
                        # remove the resource from the graph
                        del graph_processes[str(Form_resource_to_be_freed)]
                        assigned_list.remove(Form_resource_to_be_freed)
                        process_in_deadLock = []
                        resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                                           process_in_deadLock)
                        if resultDeadLock:
                            print("HandleDeadLockHere1")
                            List_resource_tobedeleted = []
                            recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                     finish_recovery, data_in_dictionary, terminated_processes_list)
                            if finish_recovery[0] == 1:
                                print(
                                    f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                process_in_deadLock = []
                                break
                    worker[1][0][1].pop(0)
                    if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                        break
                    elif left_value > 0 and len(worker[1][0][1]) > 0:
                        if str(worker[1][0][1][0]).isdigit():
                            if int(worker[1][0][1][0]) <= left_value:
                                time = time + worker[1][0][1][0]
                                left_value = left_value - worker[1][0][1][0]
                                worker[1][0][1].pop(0)
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += worker[1][0][1][0]
                                if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                    break
                            else:
                                time = time + left_value
                                worker[1][0][1][0] = worker[1][0][1][0] - left_value
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += left_value
                                left_value = 0
                                break
                ##########################################################################################
                else:
                    # if the next value is number check if the left value is grater then zero
                    if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                        break
                    elif left_value > 0 and len(worker[1][0][1]) > 0:
                        if str(worker[1][0][1][0]).isdigit():
                            if int(worker[1][0][1][0]) <= left_value:
                                time = time + worker[1][0][1][0]
                                left_value = left_value - worker[1][0][1][0]
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += worker[1][0][1][0]

                                worker[1][0][1].pop(0)
                                if len(worker[1][0][1]) > 0:
                                    if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                        break
                                else:
                                    break
                            else:
                                time = time + left_value
                                worker[1][0][1][0] = worker[1][0][1][0] - left_value
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += left_value
                                left_value = 0
                                break

            if len(worker[1][0][1]) == 0:
                worker[1].pop(0)
            if len(worker[1]) > 0:
                if worker[1][0][0] == "IO":
                    waiting.append([worker[0], worker[1], process, int(worker[1][0][1][0]) + time])
                    worker[1].pop(0)
                    if len(worker[1][0][1]) == 0:
                        worker[1].pop(0)
                    if len(worker[1]) > 0:
                        worker[1] = []
                else:
                    if len(worker[1][0][1]) > 0:
                        ready[process].append(worker)
                    else:
                        ready.pop(process)
            if len(ready[process]) == 0 and len(worker[1]) == 0:
                ready.pop(process)

            gantt.append([start_time, worker[0], time])

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

    for i in waiting:
        if i[3] <= time:
            if i[2] not in ready.keys():
                ready[i[2]] = deque()
            ready[i[2]].append([i[0], i[1]])
            waiting.remove(i)
        else:
            if len(ready) == 0:
                time = time + 1

    if len(waiting) == 0 and len(running) == 0 and len(ready) == 0 and len(waiting_res) == 0:
        break

print("the Gantt chart", gantt)
calc_turnaroundtTime(data_in_dictionary, turnaround_time, gantt)
calc_average_watingTime(waiting_time, number_process)
print("the turn around time for every process is", turnaround_time)
fp = open("output.csv", 'a')
fp.write("StartTime,ProcessType,EndType\n")
ListProcess = []
ListTime = []
for process in gantt:
    start, process, end = process
    ListTime.append(start)
    ListTime.append(end)
    ListProcess.append(process)
    ListProcess.append(process)
    fp.write(f"{start},{process},{end}\n")

fp.close()
plt.plot(ListTime,ListProcess, lw=1, color="orange", solid_capstyle="butt")
plt.yticks(range(0, int(max(ListProcess))+1, 1))
plt.xticks(range(0, int(gantt[-1][-1]), 10))
plt.xlabel("Time")
plt.ylabel("Processes")
plt.title("Gantt Chart")
plt.show()


