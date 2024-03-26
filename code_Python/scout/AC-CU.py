import random
import math
import numpy as np
import mmh3
import time
import os
import sys


def generateSeed():

    seed = random.randint(67297,4294967296)
    return seed


def generateSeeds(num):

    #生成无重复的随机数
    seeds = [random.randint(67297, 4294967296) for i in range(num)]
    while len(set(seeds)) < num:
        seeds = [random.randint(67297, 4294967296) for i in range(num)]
    return seeds    #返回的是一个num个数的随机数数组


def Read_Data(Infilename):

    Source_list = []
    Infile = open(Infilename)
    line = Infile.readline()
    while line:
        if len(line) >= 32:
            line = Infile.readline()
            continue
        else:
            temp = line.split()
            SOU_str = temp[0].split(".")
            SOU = ""
            for i in SOU_str:
                SOU += i.zfill(3)
            Source_list.append(SOU.lstrip("0"))
            line = Infile.readline()
    Infile.close()
    return Source_list


def Read_Data2(Infilename):
    Source_list = []
    Infile = open(Infilename)
    line = Infile.readline()
    while line:
        temp = line.split()
        Source_list.append(temp[0])
        line = Infile.readline()
    Infile.close()
    return Source_list


class CU:

    def __init__(self, Mem, Array_D, Counter_bits_list):
        self.Mem = Mem * 1024 * 8                    # M:整个Sketch空间
        self.Array_D = Array_D                              # 整个Sketch层数 D>=2
        self.seeds = generateSeeds(self.Array_D)            # Sketch哈希函数需要的seeds
        self.Counter_bits_list = Counter_bits_list          # 一个数组，对应各层counter size的大小
        self.CountMin = None
        self.level_i_counters = math.floor(self.Mem / self.Array_D / self.Counter_bits_list[0])
        self.CountMin = np.zeros(shape=(self.Array_D, self.level_i_counters), dtype=np.int64)
        
    def Insert(self, flow_ID):
        min_value = float("inf")
        for i in range(0, self.Array_D):
            pos = mmh3.hash(str(flow_ID), self.seeds[i], False) % self.level_i_counters 
            if self.CountMin[i][pos] < min_value:
                min_value = self.CountMin[i][pos] 
        for i in range(0, self.Array_D):
            pos = mmh3.hash(str(flow_ID), self.seeds[i], False) % self.level_i_counters 
            if self.CountMin[i][pos] == min_value and self.CountMin[i][pos] < 2 ** self.Counter_bits_list[0]-1:
                self.CountMin[i][pos] += 1

    def Query(self, flow_ID):
        min_val = 0xffffffff
        for i in range(0, self.Array_D):
            pos = mmh3.hash(str(flow_ID), self.seeds[i], False) % self.level_i_counters 
            min_val = min(min_val, self.CountMin[i][pos])
        return min_val
    
    def clean(self):
        self.CountMin = np.zeros(shape=(self.Array_D, self.level_i_counters), dtype=np.int64)


class bucket():

    def __init__(self,memory_size,cell_bits,cell_nums,P,Q,K,T):
        self.memory = memory_size* 8 * 1024
        self.cell_bits = cell_bits
        self.cell_nums = cell_nums
        self.bucket = []
        self.seed = generateSeed()
        self.P = P
        self.Q = Q
        self.K = K
        self.T = T
        self.bucket_nums =  math.floor(self.memory / (self.cell_nums * self.cell_bits))
        #self.bucket = np.zeros(shape=(self.bucket_nums, self.cell_nums, self.T+5),dtype=np.int64)
        # 当前周期为：time_windows%(T+1) ——> 0到T
        for i in range(self.bucket_nums):
            one_bucket = []
            for k in range(self.cell_nums):
                one_cell = [0]*(self.T+5)
                one_bucket.append(one_cell)
            self.bucket.append(one_bucket)


    def insert_id(self,flow_id):

        flage = False   
        pos = mmh3.hash(str(flow_id), self.seed, False) % self.bucket_nums
        for i in range(self.cell_nums):
            if str(self.bucket[pos][i][0]) == flow_id:
                flage = True
                break
        if flage == False:
            for i in range(self.cell_nums):
                if self.bucket[pos][i][0] == 0:
                    global time_windows
                    self.bucket[pos][i][0] = flow_id
                    self.bucket[pos][i][self.T+4] = time_windows
                    flage = True
                    break
        if flage == False:      # bucket满了 驱逐 (暂时不处理 bucket满了就不插入)
            global bucket_full      # 统计应该驱逐的次数
            bucket_full += 1


    def insert_value(self):

        global time_windows # 当前窗口的列值为time_windows%(T+1)+1
        for idx in range(self.bucket_nums):
            for cell in range(self.cell_nums):
                value = CUsketch.Query(str(self.bucket[idx][cell][0]))
                if self.bucket[idx][cell][0]  != 0: #and value > 7 
                    self.bucket[idx][cell][(time_windows-1)%(self.T + 1)+3] = value


    def query(self):

        global time_windows
        for i in range(self.bucket_nums):
            for j in range(self.cell_nums):
                if self.bucket[i][j][0] != 0:   # 当前cell非空时

                    zero_nums = 0
                    pos = (time_windows - 1)%(self.T + 1)+3   # 当前窗口对应的counter位置
                    for k in range(3,11):        # 首先判断当前是不是起点：除了当前时间窗口的couter，其他的counter的value全为0 则为第一次插入 即起点
                        if self.bucket[i][j][k] == 0 and k != pos:
                            zero_nums += 1
                    if zero_nums == self.T:
                        self.bucket[i][j][1] += 1
                        self.bucket[i][j][2] = pos
                    else:   # 不是起点，则遍历到起点
                        temp = time_windows
                        max_value = float("-inf")
                        #max_counter = -1

                        while (temp-1) % (self.T +1 ) + 3 != self.bucket[i][j][2]:    # 找当前counter前一个counter到起点的窗口的最大值
                            if self.bucket[i][j][(temp-2)%(self.T + 1) + 3] > max_value:
                                max_value = self.bucket[i][j][(temp-2)%(self.T + 1) + 3]
                            temp -= 1

                        if self.bucket[i][j][pos] > self.P * max_value:    # 满足增长
                            self.bucket[i][j][1] += 1
                            for m in range(3, 11):
                                if m != pos:
                                    self.bucket[i][j][m] = 0
                            self.bucket[i][j][2] = pos
                            if self.bucket[i][j][1] == self.K:  # 报告为promising flow
                                global our_result
                                global num1
                                num1 += 1
                                our_result.append([self.bucket[i][j][0],self.bucket[i][j][self.T+4],time_windows])
                                # 从当前周期重新判定是否为promising flow
                                self.bucket[i][j][1] -= 1
                        elif self.bucket[i][j][pos] < self.Q * max_value or time_windows%(self.T + 1)+3 == self.bucket[i][j][2]:    # 衰减过多 或者 没有满足增长并且已经达到了T次(当前counter下一个counter为起点)
                            for n in range(11):     # 清除cell
                                self.bucket[i][j][n] = 0



if __name__=="__main__":

    print("Programme is running!!!")
    Infilename = "E:\\research\\grade1\\D-dataset\\stack_overflow"
    Files = os.listdir(Infilename)

    for i in [5,7.5,10,12.5,15]:      # KB

        num1 = 0
        bucket_full = 0
        time_windows = 0
        our_result = []
        memory_size = i
        cell_bits = 32+3 +3 +14+14+14+14+14+14+14+14+12
        cell_nums = 4
        array_d = 3
        CM_counter_bits = [14,14,14]

        P = 1.05
        Q = 0.5
        K = 5
        T = 7

        CUsketch = CU(memory_size * 0.3,array_d,CM_counter_bits)
        oursketch = bucket(memory_size * 0.7,cell_bits,cell_nums,P,Q,K,T)     ########需要改的比例

        for index, file in enumerate(Files):
            location = Infilename + '\\' + file     # 得到父文件夹中的每个子txt文件绝对路径
            Flow_list = Read_Data2(location)
            flow_len = len(Flow_list)
            time_windows += 1 
            print("The {}th time window data is being processed!!!".format(time_windows))

            for idx,item in enumerate(Flow_list):
                # item 为字符串形式
                if CUsketch.Query(item) >= 7:           ########################需要改的变量
                    oursketch.insert_id(item)
                CUsketch.Insert(item)

            oursketch.insert_value()
            oursketch.query()
            CUsketch.clean()
            print("The {}th time window data has been processed!!!".format(time_windows))
            print("--------------------------------")

        with open("E:\\research\\grade1\\B-code\\ScoutSketch\\experiment_results\\on_stack\\straw3\\memory_"+str(i)+"KB.txt", "w") as f:
            f.write(str(our_result))
        
        print("promising flow nums =",num1)
        print("kick times =",bucket_full)