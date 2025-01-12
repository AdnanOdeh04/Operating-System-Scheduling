import matplotlib.pyplot as plt
import pandas as pd
import test
from collections import deque
import re

#This to read the data in a for of comma seperated file and store them in a chart
data = pd.read_csv("./data.csv", delimiter="|")

# index here for the dataFrame (data) which is started with value zero to track all elements in the dataFrame
# iterrow() to move through all rows in the data
data_in_dictionary = {}
for index, row in data.iterrows():
    data_in_dictionary[row['PID']] = test.Data(row['PID'], row['Arrival Time'], row['Priority'],
                                               row['Sequence of CPU and IO bursts'])
    # print(f"{row['PID']}, {row['Arrival Time']}, {row['Priority']}, {row['Sequence of CPU and IO bursts']}")
    # print(data_in_dictionary[row['PID']].calculate_total_burst())
################################All Parameters Needed##############################################################################

graph_processes = {}  # {"PID":[processes or resources]} all p or r in the list are connected directly to the process PID
assigned_list = []
ready = {}
waiting_res = {}
running = []
waiting = []
time = 0  #Total Time
time_q = 10
gantt = []  #Store the Gantt Chart
waiting_time = []  #Calculate the waiting time
turnaround_time = []  #to calcualte the turnaround time
number_process = 0
new = [i for i in data_in_dictionary.keys()]  #Added all processes in the file in a list
rosources_list = []
resource_busy = 0  #Flag
finish_recovery = 0  #Flag
process_handle_deadlock = []  #Flag used as a pointer
terminated_processes_list = {}


######################################################################################################################################
#Here the loop will move from the end to find the end time then subtract it from the arrival time and add it to the list with the name of process
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


#Here the function will find the total average time for all processes then find the avg waiting time
def calc_average_watingTime(waitingTime, number_process):
    process_waiting_time = [p[1] for p in waitingTime]
    average_waitingTime = sum(process_waiting_time) / number_process
    average_waitingTime = round(average_waitingTime, 2)
    print("the waiting time for every process is: ", waitingTime)
    print("the average waiting time is: ", average_waitingTime)


# ################################################ dead Lock Detection part ##########################################################
#Here we find whether there is a cycle or not in the graph
def deadLockDetection(m, TargetedProcess, data_dict,
                      Processes_deadlocked):
    list_processes_inDeadLock = {}
    for key in m.keys():
        dead = []
        new = key
        pointer = m[key]
        Num = 0
        F = 0
        while Num < len(m.keys()):
            if pointer not in m.keys():
                F = 1
                break
            if re.search(r"^[0-9]*$", str(pointer)):
                dead.append(pointer)
            if pointer == new:
                for process in dead:
                    priority = data_dict[int(process)].Priority
                    list_processes_inDeadLock[priority] = process
                TargetedProcess.append(list_processes_inDeadLock[max(list_processes_inDeadLock.keys())])
                Processes_deadlocked.append(dead)
                return True
            pointer = m[pointer]
            Num += 1
        if F == 1:
            continue
    return False


# #######################################################################################################################################
# ################################################ dead Lock recovery part #############################################################
def recovery(graph_processes, waiting_res, assigned_list, process_to_handle_deadlock, finished_recovery,
             data_in_dictionary, terminated_process_list):
    process_in_deadLock = []
    #each terminate operation check whether there still exist deadlock to terminate another process
    while deadLockDetection(graph_processes, process_to_handle_deadlock, data_in_dictionary, process_in_deadLock):
        #Here an arrow to point to the deadlocked process when plot it
        plt.scatter(time, worker[0], color='red')
        List_resource_tobedeleted = []
        delete_requested = []
        #All conditions below to remove process from waiting queue, assigned resources, request resources, or any pointer used
        #Also here handled whether the process is exist or not
        if graph_processes[str(process_to_handle_deadlock[0])] in waiting_res.keys():
            del waiting_res[graph_processes[str(process_to_handle_deadlock[0])]]
        for vertices in graph_processes:
            if graph_processes[vertices] == str(process_to_handle_deadlock[0]):
                List_resource_tobedeleted.append(vertices)
                if str(vertices) in assigned_list:
                    assigned_list.remove(vertices)
        while List_resource_tobedeleted:
            del graph_processes[List_resource_tobedeleted[0]]
            for vertices in graph_processes:
                if graph_processes[vertices] == str(List_resource_tobedeleted[0]):
                    delete_requested.append(vertices)
            List_resource_tobedeleted.pop(0)
        if graph_processes[str(process_to_handle_deadlock[0])] in graph_processes.keys():
            del graph_processes[str(process_to_handle_deadlock[0])]
        if str(process_to_handle_deadlock[0]) in assigned_list:
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
    #Flag is set to use it in the round robin below
    finished_recovery[0] = 1


# #######################################################################################################################################
#Here will move all processes with arrival time equals zero to the ready queue
for i in range(len(new)):
    #All the data of the processes added in a dictionary with key a priority and all other info of process
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
    #Flags defined after each loop
    process_handle_deadlock = []
    finish_recovery = []
    finish_recovery.append(0)

    for process_R in waiting_res.keys():
        if process_R not in assigned_list:
            #waiting_res is the process waiting for resources, here will check whether it ready to go to the ready queue and move it there
            #add it to ready queue and remove it from waiting resource
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
            #when the process in the deadlock terminated here this process will come to the ready queue to gurantee to start working again from the begining of this process
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
    #To detect the deadlock
    resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock, data_in_dictionary,
                                       process_in_deadLock)
    #if there is deadlock run recovery
    if resultDeadLock:
        print("--------")
        plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                     arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
        List_resource_tobedeleted = []
        recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock, finish_recovery,
                 data_in_dictionary, terminated_processes_list)
        if finish_recovery[0] == 1:
            print(
                f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
            process_in_deadLock = []
            continue
        #if there is a process in the ready go to run it to work
    if len(ready) != 0:
        resource_busy = 0
        #To find the highest priority process
        process = min(ready.keys())
        worker = ready[process].popleft()
        if len(worker[1][0][1]) == 0:
            break
        # Here when a new process comes insert it to the graph
        #To check whether the next worker will be a request or free
        testRequestFirst = re.search(r"R\[[0-9]*\]", str(worker[1][0][1][0]))
        testFreeFirst = re.search(r"F\[[0-9]*\]", str(worker[1][0][1][0]))
        # ########################## start ################################
        #if is a digit
        if str(worker[1][0][1][0]).isdigit():
            #check whether the quantom is less or equal the time quantom
            if int(worker[1][0][1][0]) <= time_q:
                start_time = time
                #update the time of the worker
                time = time + int(worker[1][0][1][0])
                #to increment the waiting time for each process
                for i in waiting_time:
                    #To check whether the process will that will be incremented not in the waiting and in the ready queue to increment time waiting
                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                        for priority in ready.values():
                            if any(proc[0] == i[0] for proc in priority):
                                i[1] += int(worker[1][0][1][0])
                #to find the left value, when the quanton keep incrementing according to the left value
                left_value = time_q - worker[1][0][1][0]
                worker[1][0][1][0] = 0
                #remove the burst of the worker
                worker[1][0][1].pop(0)
                #if the worker empty remove it to start working with another one
                if len(worker[1][0][1]) == 0:
                    worker[1].pop(0)
                #if the worker is not empty we need to keep working with the left value if exist
                else:
                    while True:
                        if len(worker[1][0][1]) == 0:
                            break
                        #if the next burst is request or free or digit
                        testRequest = re.search(r"R\[[0-9]*\]", worker[1][0][1][0])
                        testFree = re.search(r"F\[[0-9]*\]", worker[1][0][1][0])
                        if testRequest:
                            # make the Request
                            #if the request of the resource is not assigned to any process make the request and assign the resource
                            if worker[1][0][1][0] not in assigned_list:
                                graph_processes[str(worker[1][0][1][0])] = str(worker[0])
                                assigned_list.append(str(worker[1][0][1][0]))
                                #we added the assigned then remove this burst
                                worker[1][0][1].pop(0)
                                process_in_deadLock = []
                                #After making changes on the requests and assigned processes check deadlock
                                resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock,
                                                                   data_in_dictionary, process_in_deadLock)
                                if resultDeadLock:
                                    plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                                 arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                                    print("--------")
                                    List_resource_tobedeleted = []
                                    recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                             finish_recovery, data_in_dictionary, terminated_processes_list)
                                    if finish_recovery[0] == 1:
                                        print(
                                            f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                        process_in_deadLock = []
                                        break
                            else:
                                #if the resource is assinged move the process to waiting_res
                                resource_busy = 1
                                graph_processes[str(worker[0])] = str(worker[1][0][1][0])
                                waiting_res[worker[1][0][1][0]] = deque()
                                waiting_res[worker[1][0][1][0]].append([process, worker[0], worker[1]])
                                process_in_deadLock = []
                                #check deadlock after moving the process and recover it
                                resultDeadLock = deadLockDetection(graph_processes, process_handle_deadlock,
                                                                   data_in_dictionary, process_in_deadLock)
                                if resultDeadLock:
                                    plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                                 arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                                    print("--------")
                                    List_resource_tobedeleted = []
                                    recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock,
                                             finish_recovery, data_in_dictionary, terminated_processes_list)
                                    if finish_recovery[0] == 1:
                                        worker[1] = []
                                        print(
                                            f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                                        process_in_deadLock = []
                                        break
                                    #to check whether the process does not have a burst then remove it
                                if len(ready[process]) == 0:
                                    ready.pop(process)

                                break
                            #if the whole worker finished his all burst then remove it
                            if len(worker[1][0][1]) == 0:
                                worker[1].pop(0)
                                break
                            #To check whether the left value is zero and the next burst is number to move to the next time quantom
                            if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                break
                            #if the left value is not zero and there exit somthing to work check what type is it
                            elif left_value > 0 and len(worker[1][0][1]) > 0:
                                #if is it number then update the time according to the quantom and the left value
                                if str(worker[1][0][1][0]).isdigit():
                                    if int(worker[1][0][1][0]) <= left_value:
                                        time = time + worker[1][0][1][0]
                                        left_value = left_value - worker[1][0][1][0]
                                        for i in waiting_time:
                                            #To check whether the process will that will be incremented not in the waiting and in the ready queue to increment time waiting
                                            if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                                for priority in ready.values():
                                                    if any(proc[0] == i[0] for proc in priority):
                                                        i[1] += int(worker[1][0][1][0])
                                        worker[1][0][1].pop(0)
                                        if len(worker[1][0][1]) == 0:
                                            worker[1].pop(0)
                                        if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                            break
                                    else:
                                        time = time + left_value
                                        worker[1][0][1][0] = worker[1][0][1][0] - left_value
                                        for i in waiting_time:
                                            #To check whether the process will that will be incremented not in the waiting and in the ready queue to increment time waiting
                                            if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                                for priority in ready.values():
                                                    if any(proc[0] == i[0] for proc in priority):
                                                        i[1] += left_value
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
                                    plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                                 arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                                    print("--------")
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
                                #if the process is not assigned print an exception
                                print("Free for a resource not exit!")
                                exit(0)
                            #remove the worker burst
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
                                        for i in waiting_time:
                                            #To check whether the process will that will be incremented not in the waiting and in the ready queue to increment time waiting
                                            if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                                for priority in ready.values():
                                                    if any(proc[0] == i[0] for proc in priority):
                                                        i[1] += int(worker[1][0][1][0])
                                        worker[1][0][1].pop(0)
                                        if len(worker[1][0][1]) == 0:
                                            worker[1].pop(0)
                                            break
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
                    #add to gantt chart if the resouce is assinged
                    gantt.append([start_time, worker[0], time])
                    continue
                if len(worker[1]) > 0:
                    #if the next burst is IO then move to waiting to handle it
                    #in IO the code will move through the whole big loop and add one time quantom each loop to finish the whole burst of IO
                    #Behind this the code will handle the next burst
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
                #if greater than the time quantom, then add the time quantom and make updates and move to the next burst
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
        #if the burst is request or free
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
                        plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                     arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                        print("--------")
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
                        plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                     arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                        print("--------")
                        List_resource_tobedeleted = []
                        recovery(graph_processes, waiting_res, assigned_list, process_handle_deadlock, finish_recovery,
                                 data_in_dictionary, terminated_processes_list)
                        if finish_recovery[0] == 1:
                            print(
                                f"processes in the dead lock are: {process_in_deadLock[0]} and the terminated process is {process_handle_deadlock[0]}")
                            process_in_deadLock = []
                            continue
                    if len(ready[process]) == 0:
                        del ready[process]
                    continue
            elif testFreeFirst:
                #if the burst is free first then will check if the free for assigned process or not
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
                        plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                     arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                        print("--------")
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
                            plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                         arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                            print("--------")
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
                            plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                         arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
                            print("--------")
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
                                for i in waiting_time:
                                    #To check whether the process will that will be incremented not in the waiting and in the ready queue to increment time waiting
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += int(worker[1][0][1][0])
                                worker[1][0][1].pop(0)
                                if left_value == 0 and str(worker[1][0][1][0]).isdigit():
                                    break
                            else:
                                time = time + left_value
                                worker[1][0][1][0] = worker[1][0][1][0] - left_value
                                for i in waiting_time:
                                    #To check whether the process will that will be incremented not in the waiting and in the ready queue to increment time waiting
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                i[1] += left_value
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
                            print("--------")
                            plt.annotate('DeadLocked Process', xy=(time, worker[0]), xytext=(0.2, 0.2),
                                         arrowprops=dict(facecolor='yellow', ec='red', arrowstyle='->'))
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
                                for i in waiting_time:
                                    if i[0] != worker[0] and all(w[0] != i[0] for w in waiting):
                                        for priority in ready.values():
                                            if any(proc[0] == i[0] for proc in priority):
                                                print(time)
                                                i[1] += worker[1][0][1][0]
                                worker[1][0][1].pop(0)
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
    #check whether the arrival time of the process comes and add it to the readu queue
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
    #if the processes finish in the waiting then remove it from waiting and add it to the ready
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
fp = open("output.csv", 'w')
fp.write("StartTime,ProcessType,EndType\n")
fp.close()
fp = open("output.csv", 'a')
ListProcess = []
ListTime = []
for process in gantt:
    start, process, end = process
    if int(start) != int(end):
        ListTime.append(start)
        ListTime.append(end)
        ListProcess.append(process)
        ListProcess.append(process)
        fp.write(f"{start},{process},{end}\n")

fp.close()
plt.plot(ListTime, ListProcess, lw=1, color="orange", solid_capstyle="butt")
plt.yticks(range(0, int(max(ListProcess)) + 1, 1))
plt.xticks(range(0, int(gantt[-1][-1]), time_q))
plt.xlabel("Time")
plt.ylabel("Processes")
plt.title("Gantt Chart")
plt.show()
