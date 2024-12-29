import re
import numpy as np


class Data:
    PID = 0
    Arrival_Time = 0
    Priority = 0
    Sequence_of_CPU_and_IO_bursts = []
    Check = 0

    def __init__(self, PID, Arrival_Time, Priority, Sequence_of_CPU_and_IO_bursts, Check=0):
        self.PID = PID
        self.Arrival_Time = Arrival_Time
        self.Priority = Priority
        self.Sequence_of_CPU_and_IO_bursts = Sequence_of_CPU_and_IO_bursts
        self.Check = Check

    def printData(self):
        print(
            f"{self.PID}, {self.Arrival_Time}, {self.Priority}, {self.Sequence_of_CPU_and_IO_bursts}, Check->{self.Check}")

    def calculate_total_burst(self):
        newList = self.Sequence_of_CPU_and_IO_bursts.split()
        list_total_Bursts = []
        list_all_Bursts = []
        sum = 0
        for i in newList:
            x = re.search(r"{.*}", i)
            val = list(x.span())
            new = (i[val[0] + 1:val[1] - 1]).split(",")
            list_total_Bursts = [c for c in new if c.isdigit()]
            npList = np.array(list_total_Bursts, dtype=int)
            sum = np.sum(npList)
            y = re.search(r".*{", i)
            valType = list(y.span())
            Type = i[valType[0]:valType[1] - 1]

            list_all_Bursts.append([Type,int(sum)])
        return list_all_Bursts
