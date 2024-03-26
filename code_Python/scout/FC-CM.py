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

class Count_Min2:
    def __init__(self, Mem, Array_D, Counter_bits_list):
        self.Mem = Mem * 1024 * 8                    # M:整个Sketch空间
        self.Array_D = Array_D                              # 整个Sketch层数 D>=2
        self.seeds = generateSeeds(self.Array_D)            # Sketch哈希函数需要的seeds
        self.Counter_bits_list = Counter_bits_list          # 一个数组，对应各层counter size的大小
        self.CountMin = None
        self.level_i_counters = math.floor(self.Mem / self.Array_D / self.Counter_bits_list[0])
        self.CountMin = np.zeros(shape=(self.Array_D, self.level_i_counters), dtype=np.int64)
        
    def Insert(self, flow_ID):
        for i in range(0, self.Array_D):
            pos = mmh3.hash(str(flow_ID), self.seeds[i], False) % self.level_i_counters 
            self.CountMin[i][pos] += 1

    def Query(self, flow_ID):
        min_val = 0xffffffff
        for i in range(0, self.Array_D):
            pos = mmh3.hash(str(flow_ID), self.seeds[i], False) % self.level_i_counters 
            min_val = min(min_val, self.CountMin[i][pos])
        return min_val
    
    def clean(self):
        self.CountMin = np.zeros(shape=(self.Array_D, self.level_i_counters), dtype=np.int64)


class scout_sketch():  # headhunter
    
    def __init__(self,memory_size,cell_bits,cell_nums,P,Q,K,T):
        self.mem = memory_size * 1024 * 8
        self.cell_bits = cell_bits
        self.cell_nums = cell_nums
        self.seed = generateSeed()
        self.scout = []
        self.P = P
        self.Q = Q
        self.K = K
        self.T = T
        self.bucket_nums = math.floor(self.mem / (self.cell_nums * self.cell_bits))

        #self.scout = np.zeros(shape=(self.bucket_nums, self.cell_nums, 6), dtype=np.int64)
        for i in range(self.bucket_nums):
            one_bucket = []
            for k in range(self.cell_nums):
                one_cell = [0]*(6)
                one_bucket.append(one_cell)
            self.scout.append(one_bucket)


    def insert_id(self,flow_id):

        flage = False   
        pos = mmh3.hash(str(flow_id), self.seed, False) % self.bucket_nums
        for i in range(self.cell_nums):
            if str(self.scout[pos][i][0]) == flow_id:
                flage = True
                break
        if flage == False:
            for i in range(self.cell_nums):
                if self.scout[pos][i][0] == 0:
                    self.scout[pos][i][0] = flow_id
                    global time_windows
                    self.scout[pos][i][5] = time_windows
                    flage = True
                    break
        if flage == False:      # bucket满了 驱逐 (暂时不处理 bucket满了就不插入)
            global bucket_full      # 统计应该驱逐的次数
            bucket_full += 1


    def query(self):        # 每周期末的查询、判定 以及对current value清零
        for idx in range(self.bucket_nums):
            for cell in range(self.cell_nums):
                if self.scout[idx][cell][0] != 0:
                    global time_windows
                    value = cmsketch.Query(str(self.scout[idx][cell][0]))
                    #print(value)

                    # if str(self.scout[idx][cell][0]) == "82096243186":
                    #     if time_windows>2300 and time_windows <2400:
                    #         print(time_windows)
                    #         print(value)

                    if value > self.scout[idx][cell][2] * self.P:     # 满足增长率P
                        self.scout[idx][cell][3] += 1
                        self.scout[idx][cell][4] = 0
                        self.scout[idx][cell][2] = value
                        if self.scout[idx][cell][3] == self.K:   # 达到成功阈值
                            # 报告为promising flow
                            global our_result
                            global num1
                            num1 += 1
                            our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows])
                            # 从当前周期重新判定是否为promising flow
                            self.scout[idx][cell][3] -= 1
                    elif value < self.scout[idx][cell][2] * self.Q:  # 衰减过多
                        # （存在的问题为：驱逐清出还是当作第一个周期测量）
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0
                    else:
                        self.scout[idx][cell][4] += 1
                        if value > self.scout[idx][cell][2]:      # 当前周期微增
                            self.scout[idx][cell][2] = value
                        if self.scout[idx][cell][4] == self.T:      # 达到失败阈值 直接踢出
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0


if __name__=="__main__":

    # 单个CM+bucket(不保留current_value)

    print("Programme is running!!!")
    Infilename = "E:\\research\\grade1\\D-dataset\\stack_overflow"
    Files = os.listdir(Infilename)

    for i in [5,7.5,10,12.5,15]:      # KB

        num1 = 0
        bucket_full = 0
        time_windows = 0
        our_result = []
        memory_size = i
        cell_bits = 32 + 14 + 3 + 3 +12
        cell_nums = 4
        array_d = 3
        CM_counter_bits = [14,14,14]

        P = 1.05
        Q = 0.5
        K = 5
        T = 7

        cmsketch = Count_Min2(memory_size*0.3,array_d,CM_counter_bits)
        scoutsketch = scout_sketch(memory_size*0.7,cell_bits,cell_nums,P,Q,K,T)     ########需要改的比例
        #nums = set()
        #print("READING")
        for index, file in enumerate(Files):
            location = Infilename + '\\' + file     # 得到父文件夹中的每个子txt文件绝对路径
            Flow_list = Read_Data2(location)
            flow_len = len(Flow_list)
     
            print("The {}th time window data is being processed!!!".format(index))
            time_windows += 1

            for item in Flow_list:
                # item 为字符串形式
                if cmsketch.Query(item) >= 7:           ########################需要改的变量
                    #nums.add(item)
                    scoutsketch.insert_id(item)
                cmsketch.Insert(item)

            scoutsketch.query()
            cmsketch.clean()

            print("The {}th time window data has been processed!!!".format(index))
            print("--------------------------------")

        #print(len(nums))

        with open("E:\\research\\grade1\\B-code\\ScoutSketch\\experiment_results\\on_stack\\straw2\\memory"+str(i)+"KB.txt", "w") as f:
            f.write(str(our_result))
        
        print("promising flow nums =",num1)
        print("kick times =",bucket_full)