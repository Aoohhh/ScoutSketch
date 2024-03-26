# 先遍历bucket

import random
import math
import numpy as np
import mmh3
import time
import os
import sys
import re

def generateSeed():

    seed = random.randint(67297,4294967296)
    return seed


def generateSeeds(num):

    #生成无重复的随机数
    seeds = [random.randint(67297, 4294967296) for i in range(num)]
    while len(set(seeds)) < num:
        seeds = [random.randint(67297, 4294967296) for i in range(num)]
    return seeds    #返回的是一个num个数的随机数数组



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

class filter():     
    

    def __init__(self, Mem,cold_filter_Counter_bits,d):

        self.Mem = Mem * 1024 * 8                    # M:整个Sketch空间
        self.seed_nums = d
        self.filter_seeds = generateSeeds(self.seed_nums)            # Sketch哈希函数需要的seeds

        self.cold_filter_Counter_bits = cold_filter_Counter_bits         # 对应counter 所占的bit数
        self.counter_nums = math.floor(self.Mem/self.cold_filter_Counter_bits)
        self.coldfilter = []
        self.coldfilter = np.zeros(self.counter_nums,dtype=np.int64)


    def Insert_cold_filter(self, flow_ID):
        # CU
        pos = [0]*self.seed_nums
        temp = []
        for i in range(self.seed_nums):
            pos[i] = mmh3.hash(str(flow_ID), self.filter_seeds[i], False) % len(self.coldfilter)
            temp.append(self.coldfilter[pos[i]])
        temp_min = min(temp)
        if temp_min == 2 ** self.cold_filter_Counter_bits - 1:
            scoutsketch.insert(flow_ID)             # stage2入口

        for j in range(self.seed_nums):
            if self.coldfilter[pos[j]] == temp_min and self.coldfilter[pos[j]] < 2 ** self.cold_filter_Counter_bits - 1:
                self.coldfilter[pos[j]] += 1


    def Insert_CM_filter(self,flow_ID):

        pos = [0]*self.seed_nums
        flage = False
        for i in range(self.seed_nums):
            pos[i] = mmh3.hash(str(flow_ID), self.filter_seeds[i], False) % len(self.coldfilter)
            if self.coldfilter[pos[i]] == 2 ** self.cold_filter_Counter_bits - 1:
                continue
            else:
                flage = True
                self.coldfilter[pos[i]] += 1
        if flage == False:
            scoutsketch.insert(flow_ID)             # stage2入口


    def clean(self):        # 每周期刷新filter

        self.coldfilter = np.zeros(self.counter_nums,dtype=np.int64)


class scout_sketch():  # headhunter
    
    def __init__(self,memory_size,cell_bits,counterbits,cell_nums,P,Q,K,T,judge,protect):
        self.mem = memory_size * 1024 * 8
        self.cell_bits = cell_bits
        self.cell_nums = cell_nums
        self.counterbits = counterbits
        self.seed = generateSeed()
        self.scout = []
        self.P = P
        self.Q = Q
        self.K = K
        self.T = T
        self.judge = judge
        self.protect = protect
        self.bucket_nums = math.floor(self.mem / (self.cell_nums * self.cell_bits))
        for i in range(self.bucket_nums):
            one_bucket = []
            for cell_number in range(self.cell_nums):
                one_cell = [0]*6
                one_bucket.append(one_cell)
            self.scout.append(one_bucket)


    def checkinsert(self,flow_id):
        exist = False
        pos = mmh3.hash(str(flow_id), self.seed, False) % len(self.scout)
        for i in range(self.cell_nums):
            if self.scout[pos][i][0] == flow_id:
                self.scout[pos][i][1] += 1
                exist = True
                break
        if exist == False:        
            Filter.Insert_CM_filter(flow_id)



    def insert(self,flow_id):
        global time_windows
        flage = False   
        pos = mmh3.hash(str(flow_id), self.seed, False) % len(self.scout)

        kickcell = -1
        mindelta = float("-inf")

        for i in range(self.cell_nums):
            if self.scout[pos][i][0] != 0:
                if self.scout[pos][i][3] != 0:
                    interval = time_windows - self.scout[pos][i][5]
                    delta = interval / self.scout[pos][i][3]
                    if interval > self.protect and delta > mindelta:
                        kickcell = i
                        mindelta = delta

        for i in range(self.cell_nums):
            if self.scout[pos][i][0] == 0:      # 
                self.scout[pos][i][0] = flow_id
                self.scout[pos][i][1] = 2 ** counter_bits
                self.scout[pos][i][3] = 0
                self.scout[pos][i][5] = time_windows
                flage = True
                break


        if flage == False:      # bucket满了 驱逐
            global bucket_full      # 统计应该驱逐的次数
            if kickcell != -1 and mindelta >= self.judge:        # 参数0.5
                    self.scout[pos][kickcell][0] = flow_id
                    self.scout[pos][kickcell][1] = 2 ** counter_bits
                    self.scout[pos][kickcell][2] = 0
                    self.scout[pos][kickcell][3] = 0
                    self.scout[pos][kickcell][4] = 0
                    self.scout[pos][kickcell][5] = time_windows
            else:
                bucket_full += 1


    def query(self):        # 每周期末的查询、判定 以及对current value清零
        global time_windows
        for idx in range(self.bucket_nums):
            for cell in range(self.cell_nums):
                if self.scout[idx][cell][0] != 0: 

                    if self.scout[idx][cell][1] > self.scout[idx][cell][2] * self.P:     # 满足增长率P
                        self.scout[idx][cell][3] += 1
                        self.scout[idx][cell][4] = 0
                        self.scout[idx][cell][2] = self.scout[idx][cell][1]
                   
                        if self.scout[idx][cell][3] == self.K:   # 达到成功阈值
                            # 报告为promising flow

                            global our_result
                            global num1
                            num1 += 1
                            our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows])
                            # 从当前周期重新判定是否为promising flow
                            self.scout[idx][cell][3] -= 1
                    elif self.scout[idx][cell][1] < self.scout[idx][cell][2] * self.Q:  # 衰减过多
                        # （存在的问题为：驱逐清出还是当作第一个周期测量）
                        self.scout[idx][cell][0] = 0        ####################################################test
                        self.scout[idx][cell][2] = 0
                        self.scout[idx][cell][3] = 0
                        self.scout[idx][cell][4] = 0
                    else:
                        self.scout[idx][cell][4] += 1   # 当前周期微增 不更新最大值
                        if self.scout[idx][cell][4] == self.T:      # 达到失败阈值 直接踢出
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0

                    self.scout[idx][cell][1] = 0    # 每周期对Current_value置零


if __name__=="__main__":
    # (先查bucket)

    print("Programme is running!!!")
    Infilename = "E:\\research\\grade1\\D-dataset\\stack_overflow"
    Files = os.listdir(Infilename)

    for memory in [50]:      # KB
        a = time.time()
        timesum = 0
        for parameter_filter_ratio in [0.3]:
            for d in [2]:
                for cellnums in [4]:
                    memory_size = memory
                    cell_bits = 32+14+14+4+3+12
                    cell_nums = cellnums
                    counter_bits = 3
                    for K_value in [10]:
                        for q in [0.7]:                            
                            P = 1.2
                            Q = q
                            K = 5
                            T = K_value
                            for judge in [3]:
                                num1 = 0
                                bucket_full = 0
                                time_windows = 0
                                our_result = []
                                sum = 0
                                Filter = filter(memory_size*parameter_filter_ratio,counter_bits,d)   # filter比例最优0.3
                                scoutsketch = scout_sketch(memory_size*(1-parameter_filter_ratio),cell_bits,counter_bits, cell_nums,P,Q,K,T,judge,5)
                                print("new start")

                                for file in Files:
                                    location = Infilename + '\\' + file     # 得到父文件夹中的每个子txt文件绝对路径
                                    Flow_list = Read_Data2(location)

                                    #print("The {}th time window data is being processed!!!".format(time_windows))
                                    for item in Flow_list:
                                    
                                        scoutsketch.checkinsert(item)
                                    scoutsketch.query()
                                    Filter.clean()
                                    #print("The {}th time window data has been processed!!!".format(index))
                                    #print("--------------------------------")

                                with open("E:\\research\grade1\\B-code\\ScoutSketch\\experiment_results\\stack_test\\memory_"+str(memory)+".txt", "w") as f:
                                    f.write(str(our_result))
                                
                                print(num1)
                                print(bucket_full)
                                bucket_full = 0
                   