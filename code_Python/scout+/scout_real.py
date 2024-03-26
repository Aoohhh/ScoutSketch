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


class detect_real():  # headhunter
    
    def __init__(self,memory_size,cell_bits,cell_nums,P,Q,K,T,decline_threshold,increase_threshold):
        self.mem = memory_size * 1024 * 8
        self.cell_bits = cell_bits
        self.cell_nums = cell_nums
        self.seed = generateSeed()
        self.scout = []
        self.P = P
        self.Q = Q
        self.K = K
        self.T = T
        self.decline_threshold = decline_threshold
        self.increase_threshold = increase_threshold
        self.bucket_nums = math.floor(self.mem / (self.cell_nums * self.cell_bits))
        for i in range(self.bucket_nums):
            one_bucket = []
            for cell_number in range(self.cell_nums):
                one_cell = [0]*8
                one_bucket.append(one_cell)
            self.scout.append(one_bucket)
    
    
    def checkinsert(self,flow_id,value):
        pos = mmh3.hash(str(flow_id), self.seed, False) % len(self.scout)
        for i in range(self.cell_nums):
            if self.scout[pos][i][0] == flow_id:
                if self.scout[pos][i][1] == 0:      # 每个周期第一次的插入都该加上filter的值
                    self.scout[pos][i][1] += value


    def insert(self,flow_id,value):

        flage = False
        pos = mmh3.hash(str(flow_id), self.seed, False) % len(self.scout)
        for i in range(self.cell_nums):
            if self.scout[pos][i][0] == flow_id:       # bucket中已经保存
                self.scout[pos][i][1] += value
                flage = True
                break
        if flage == False:
            for i in range(self.cell_nums):
                if self.scout[pos][i][0] == 0:      # bucket中未保存 但有空位
                    self.scout[pos][i][0] = flow_id
                    self.scout[pos][i][1] = value     # 具体值需要改变
                    self.scout[pos][i][5] = time_windows
                    flage = True
                    break
        
        if flage == False:      # bucket满了 驱逐
            global real_full
            real_full += 1


    def query(self):        # 每周期末的查询、判定 以及对current value清零


        global time_windows
        global our_result
        global num_promising_flows_1
        global num_promising_flows_2
        for idx in range(self.bucket_nums):
            for cell in range(self.cell_nums):
                if self.scout[idx][cell][0] != 0: 

                    if self.scout[idx][cell][1] > self.scout[idx][cell][2] * self.P:     # 
                        if self.scout[idx][cell][1]<self.increase_threshold:   # 16是filter的阈值 
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][1] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0
                            self.scout[idx][cell][6] = 0
                            self.scout[idx][cell][7] = 0
                            continue
                        
                        if self.scout[idx][cell][6] == 0:       #此前为起点或上升
                            self.scout[idx][cell][3] += 1
                        else:   # 此前为下降 当前变为了升 ——————》需要改变起点**
                            if self.scout[idx][cell][2] < self.increase_threshold:   # 16是filter的阈值
                                self.scout[idx][cell][3] = 1
                                self.scout[idx][cell][5] = time_windows     # 改变起点时间 *********************
                            else:
                                self.scout[idx][cell][3] = 2
                                self.scout[idx][cell][5] = self.scout[idx][cell][7]     # 改变起点时间 *********************
                        self.scout[idx][cell][2] = self.scout[idx][cell][1]     # 改变参考值
                        self.scout[idx][cell][4] = 0    # 刷新失败次数
                        self.scout[idx][cell][6] = 0
                            
                        if self.scout[idx][cell][3] == self.K:   # 达到成功阈值
                            # 报告为promising flow
                            num_promising_flows_1 += 1
                            our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows,self.scout[idx][cell][6]])
                            # 从当前周期重新判定是否为promising flow
                            self.scout[idx][cell][3] -= 1
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

                        self.scout[idx][cell][4] = 0    # 刷新失败次数
                        if self.scout[idx][cell][6] == 0:   # 此前为起点或上升
                            if self.scout[idx][cell][2] < self.decline_threshold:   # 太小了 不可以继续降 但是需要检查最新值是否大于升的阈值 否则清空
                                if self.scout[idx][cell][1]>=self.increase_threshold:  # 把当前点作为一个新的起点
                                    self.scout[idx][cell][2] = self.scout[idx][cell][1]
                                    self.scout[idx][cell][1] = 0
                                    self.scout[idx][cell][3] = 1
                                    self.scout[idx][cell][4] = 0
                                    self.scout[idx][cell][5] = time_windows
                                    self.scout[idx][cell][6] = 0
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
                            self.scout[idx][cell][2] = self.scout[idx][cell][1]
                            self.scout[idx][cell][3] = 2
                            self.scout[idx][cell][6] = 1
                            self.scout[idx][cell][7] = time_windows
                        else:       # 此前为降
                            self.scout[idx][cell][3] += 1
                            self.scout[idx][cell][2] = self.scout[idx][cell][1]
                            if self.scout[idx][cell][3] == self.K:
                                num_promising_flows_2 += 1
                                our_result.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows,self.scout[idx][cell][6]])
                                # 从当前周期重新判定是否为promising flow
                                self.scout[idx][cell][3] -= 1
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
                            continue
                    self.scout[idx][cell][1] = 0

if __name__=="__main__":

    print("Programme is running!!!")
    Infilename = "E:\\research\\grade1\\D-dataset\\CAIDA2019\\1w_3000"
    Files = os.listdir(Infilename)

    cell_bits = 32+14+14+4+4+12+1+12
    cell_nums = 32

    num_promising_flows_1 = 0
    num_promising_flows_2 = 0
    increase_threshold = 2**4
    decline_threshold = 64
    for T_value in [10]:
        time_windows = 0    # 当前窗口
        our_result = []     # 用于保存结果
        num2 = 0        # 保存出现的promising总和
        real_full = 0       # bucket满了的次数
        P = 1.05
        Q = 0.95
        K = 5
        T = T_value

        scoutsketch_real = detect_real(500,cell_bits,cell_nums,P,Q,K,T,decline_threshold,increase_threshold)

        #print(k_value)

        for index, file in enumerate(Files):
            location = Infilename + '\\' + file     # 得到父文件夹中的每个子txt文件绝对路径
            Flow_list = Read_Data2(location)
 
            time_windows += 1

           # print("The {}th time window data is being processed!!!".format(time_windows))

            real_key_value = {}

            for item in Flow_list:
                if item in real_key_value:
                    real_key_value[item] += 1
                else:
                    real_key_value[item] = 1

            for key,values in real_key_value.items():       # 遍历当前窗口的真实值字典   

                if values <increase_threshold:     #不满足阈值的只检查有没有已经被保存在bucket中 有则加 无则pass
                    scoutsketch_real.checkinsert(key,values)
                else:         # 将size满足大小的插入无限空间的sketch ————》保证输出为groundtruth
                    scoutsketch_real.insert(key,values)

            scoutsketch_real.query()

            print("The {}th time window data has been processed!!!".format(time_windows))
            #print("--------------------------------")

        with open("E:\\research\\grade1\\result\\scout(+-1w)_True.txt", "w") as f:
            f.write(str(our_result))

        if real_full != 0:
            print(real_full)
            print("ERROE-full")
            sys.exit()

        print("increase : ", num_promising_flows_1)
        print("decrease : ", num_promising_flows_2)
        print("run over successfully!!!")