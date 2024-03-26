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

class filter():     # 先查filter 后查bucket
    

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
    
    def __init__(self,memory_size,cell_bits,counterbits,cell_nums,P,Q,K,T,judge,protect,decline_threshold):
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
        self.decline_threshold = decline_threshold
        self.bucket_nums = math.floor(self.mem / (self.cell_nums * self.cell_bits))
        for i in range(self.bucket_nums):
            one_bucket = []
            for cell_number in range(self.cell_nums):
                one_cell = [0]*8
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


    # def query(self):        # 每周期末的查询、判定 以及对current value清零
    #     global time_windows
    #     global our_result
    #     global num_promising_flows_1
    #     global num_promising_flows_2
    #     for idx in range(self.bucket_nums):
    #         for cell in range(self.cell_nums):
    #             if self.scout[idx][cell][0] != 0: 

    #                 # debug
    #                 if time_windows > 1715 and self.scout[idx][cell][0] == '189.55.242.120':
    #                     print("TIME : ", time_windows)
    #                     print(self.scout[idx][cell])
                    
    #                 if time_windows > 1730:
    #                     sys.exit()
    #                 ##############################################

    #                 if self.scout[idx][cell][1] > self.scout[idx][cell][2] * self.P:     # 
                        
    #                     self.scout[idx][cell][4] = 0    # 刷新失败次数
    #                     self.scout[idx][cell][2] = self.scout[idx][cell][1]     # 改变参考值
                        
    #                     if self.scout[idx][cell][6] == 0:       #此前为起点或上升
    #                         self.scout[idx][cell][3] += 1
    #                     else:   # 此前为下降 当前变为了升 ——————》需要改变起点**
    #                         self.scout[idx][cell][3] = 2
    #                         self.scout[idx][cell][6] = 0
    #                         self.scout[idx][cell][5] = self.scout[idx][cell][7]     # 改变起点时间 *********************
    #                     if self.scout[idx][cell][3] == self.K:   # 达到成功阈值
    #                         # 报告为promising flow
    #                         num_promising_flows_1 += 1
    #                         our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows,self.scout[idx][cell][6]])
    #                         # 从当前周期重新判定是否为promising flow
    #                         self.scout[idx][cell][3] -= 1
    #                     self.scout[idx][cell][7] = time_windows     # 在最后改变最近一次满足条件的增或减


    #                 elif self.scout[idx][cell][1] < self.scout[idx][cell][2] * self.Q:

    #                     if self.scout[idx][cell][1] == 0:   # 降为0了之后不能再降了， 直接清空
    #                         self.scout[idx][cell][0] = 0
    #                         self.scout[idx][cell][1] = 0
    #                         self.scout[idx][cell][2] = 0
    #                         self.scout[idx][cell][3] = 0
    #                         self.scout[idx][cell][4] = 0
    #                         self.scout[idx][cell][5] = 0
    #                         self.scout[idx][cell][6] = 0
    #                         self.scout[idx][cell][7] = 0
    #                         continue

    #                     self.scout[idx][cell][4] = 0    # 刷新失败次数
    #                     if self.scout[idx][cell][6] == 0:   # 此前为起点或上升
    #                         if self.scout[idx][cell][2] < self.decline_threshold:
    #                             self.scout[idx][cell][0] = 0
    #                             self.scout[idx][cell][1] = 0
    #                             self.scout[idx][cell][2] = 0
    #                             self.scout[idx][cell][3] = 0
    #                             # self.scout[idx][cell][4] = 0
    #                             self.scout[idx][cell][5] = 0
    #                             self.scout[idx][cell][6] = 0
    #                             self.scout[idx][cell][7] = 0
    #                             continue
    #                         if self.scout[idx][cell][3] != 1: # 不是起点 需要改变起点位置
    #                             self.scout[idx][cell][5] = self.scout[idx][cell][7]
    #                         self.scout[idx][cell][2] = self.scout[idx][cell][1]
    #                         self.scout[idx][cell][3] = 2
    #                         self.scout[idx][cell][6] = 1
    #                         self.scout[idx][cell][7] = time_windows
    #                     else:       # 此前为降
    #                         self.scout[idx][cell][3] += 1
    #                         self.scout[idx][cell][2] = self.scout[idx][cell][1]
    #                         if self.scout[idx][cell][3] == self.K:
    #                             # 报告为promising flow
    #                             # global our_result
    #                             # global num_promising_flows
    #                             num_promising_flows_2 += 1
    #                             our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows,self.scout[idx][cell][6]])
    #                             #print(self.scout[idx][cell])
    #                             # 从当前周期重新判定是否为promising flow
    #                             self.scout[idx][cell][3] -= 1
    #                     self.scout[idx][cell][7] = time_windows     # 在最后改变最近一次满足条件的增或减
    #                 else:
    #                     self.scout[idx][cell][4] += 1
    #                     if self.scout[idx][cell][4] == self.T:
    #                         self.scout[idx][cell][0] = 0
    #                         self.scout[idx][cell][1] = 0
    #                         self.scout[idx][cell][2] = 0
    #                         self.scout[idx][cell][3] = 0
    #                         self.scout[idx][cell][4] = 0
    #                         self.scout[idx][cell][5] = 0
    #                         self.scout[idx][cell][6] = 0
    #                         continue
    #                 self.scout[idx][cell][1] = 0
    
    
    def query(self):        # 每周期末的查询、判定 以及对current value清零


        global time_windows
        global our_result
        global num_promising_flows_1
        global num_promising_flows_2
        for idx in range(self.bucket_nums):
            for cell in range(self.cell_nums):
                if self.scout[idx][cell][0] != 0: 

                    if self.scout[idx][cell][1] > self.scout[idx][cell][2] * self.P:     # 
                        if self.scout[idx][cell][1]<2**self.counterbits:   # 16是filter的阈值 # 可能导致bug（起点的值太小，不可以当起点）
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][1] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0
                            self.scout[idx][cell][6] = 0    # flage
                            self.scout[idx][cell][7] = 0
                            continue
                        
                        if self.scout[idx][cell][6] == 0:       #此前为起点或上升
                            self.scout[idx][cell][3] += 1
                            if self.scout[idx][cell][3] == self.K:   # 达到成功阈值
                                # 报告为promising flow
                                num_promising_flows_1 += 1
                                our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows,self.scout[idx][cell][6]])
                                # 从当前周期重新判定是否为promising flow
                                self.scout[idx][cell][3] -= 1
                        else:   # 此前为下降 当前变为了升 ——————》需要改变起点**
                            # 可能导致bug（起点的值太小，不可以当起点）
                            if self.scout[idx][cell][2] < 2**self.counterbits:   # 16是filter的阈值
                                self.scout[idx][cell][3] = 1
                                self.scout[idx][cell][5] = time_windows     # 改变起点时间 *********************
                            else:
                                self.scout[idx][cell][3] = 2
                                self.scout[idx][cell][5] = self.scout[idx][cell][7]     # 改变起点时间 *********************
                            self.scout[idx][cell][6] = 0
                        self.scout[idx][cell][2] = self.scout[idx][cell][1]     # 改变参考值
                        self.scout[idx][cell][4] = 0    # 刷新失败次数
                        self.scout[idx][cell][7] = time_windows     # 在最后改变最近一次满足条件的增或减

                    elif self.scout[idx][cell][1] < self.scout[idx][cell][2] * self.Q:

                        if self.scout[idx][cell][1] == 0:   # 降为0了之后不能再降了， 直接清空
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][1] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0
                            self.scout[idx][cell][6] = 0
                            self.scout[idx][cell][7] = 0
                            continue

                        if self.scout[idx][cell][6] == 0:   # 此前为起点或上升
                            if self.scout[idx][cell][2] < self.decline_threshold:   # 太小了 不可以继续降 但是需要检查最新值是否大于升的阈值 否则清空
                                if self.scout[idx][cell][1]>=2**self.counterbits:  # 把当前点作为一个新的起点
                                    self.scout[idx][cell][2] = self.scout[idx][cell][1]
                                    self.scout[idx][cell][1] = 0
                                    self.scout[idx][cell][3] = 1
                                    self.scout[idx][cell][4] = 0
                                    self.scout[idx][cell][5] = time_windows
                                    self.scout[idx][cell][7] = time_windows
                                    continue
                                else:
                                    self.scout[idx][cell][0] = 0
                                    self.scout[idx][cell][1] = 0
                                    self.scout[idx][cell][2] = 0
                                    self.scout[idx][cell][3] = 0
                                    self.scout[idx][cell][5] = 0
                                    self.scout[idx][cell][6] = 0
                                    self.scout[idx][cell][7] = 0
                                    continue
                            if self.scout[idx][cell][3] != 1: # 不是起点 需要改变起点位置
                                self.scout[idx][cell][5] = self.scout[idx][cell][7]
                            
                            self.scout[idx][cell][3] = 2
                            self.scout[idx][cell][6] = 1
                        else:       # 此前为降
                            self.scout[idx][cell][3] += 1
                            if self.scout[idx][cell][3] == self.K:
                                num_promising_flows_2 += 1
                                our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows,self.scout[idx][cell][6]])
                                # 从当前周期重新判定是否为promising flow
                                self.scout[idx][cell][3] -= 1
                        self.scout[idx][cell][2] = self.scout[idx][cell][1]
                        self.scout[idx][cell][4] = 0    # 刷新失败次数
                        self.scout[idx][cell][7] = time_windows     # 在最后改变最近一次满足条件的增或减
                    else:
                        self.scout[idx][cell][4] += 1
                        if self.scout[idx][cell][4] == self.T:
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][1] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0
                            self.scout[idx][cell][6] = 0
                            self.scout[idx][cell][7] = 0
                            continue
                    self.scout[idx][cell][1] = 0



if __name__=="__main__":
    # (先查bucket)

    print("Programme is running!!!")
    Infilename = "E:\\research\\grade1\\D-dataset\\CAIDA2019\\1w_3000"
    Files = os.listdir(Infilename)

    cell_bits = 32+15+15+4+4+12+1+12
    counter_bits = 4
    decline_threshold = 64
    for memory in [1000]:      # KB
        memory_size = memory
        for parameter_filter_ratio in [0.3]:
            for d in [2]:
                for cellnums in [4]:
                    cell_nums = cellnums
                    for K_value in [5]:
                        K = K_value
                        for T_value in [10]:
                            T = T_value
                            for p in [1.05]:
                                P = p
                            for q in [0.95]:                            
                                Q = q
                                for judge in [3]:
                                    num_promising_flows_1 = 0
                                    num_promising_flows_2 = 0
                                    bucket_full = 0
                                    time_windows = 0
                                    our_result = []
                                    Filter = filter(memory_size*parameter_filter_ratio,counter_bits,d)   # filter比例最优0.3
                                    scoutsketch = scout_sketch(memory_size*(1-parameter_filter_ratio),cell_bits,counter_bits, cell_nums,P,Q,K,T,judge,5,decline_threshold)
                                    print("new start")

                                    for file in Files:
                                        location = Infilename + '\\' + file     # 得到父文件夹中的每个子txt文件绝对路径
                                        Flow_list = Read_Data2(location)

                                        time_windows += 1     
                                        print("The {}th time window data is being processed!!!".format(time_windows))
                                        for item in Flow_list:
                                            scoutsketch.checkinsert(item)
        
                                        scoutsketch.query()
        
                                        Filter.clean()
                                        #sys.exit()
                                        #print("The {}th time window data has been processed!!!".format(index))
                                        #print("--------------------------------")

                                    with open("E:\\research\\grade1\\result\\(1M)memory_"+str(memory)+".txt", "w") as f:
                                        f.write(str(our_result))
                                    
                                    print("increase : ",num_promising_flows_1)
                                    print("decrease : ",num_promising_flows_2)

                                    print(bucket_full)
                                    bucket_full = 0
