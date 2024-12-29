class Data:
    PID = 0
    Arrival_Time = 0
    Priority = 0
    Sequence_of_CPU_and_IO_bursts = []
    Check=0

    def __init__(self, PID, Arrival_Time, Priority, Sequence_of_CPU_and_IO_bursts, Check):
        self.PID = PID
        self.Arrival_Time = Arrival_Time
        self.Priority = Priority
        self.Sequence_of_CPU_and_IO_bursts = Sequence_of_CPU_and_IO_bursts
        self.Check = Check



test1 = Data(1, 1, 10, [['C', 'R(1)', 50, 'F(1)']])
print(test1.Sequence_of_CPU_and_IO_bursts)