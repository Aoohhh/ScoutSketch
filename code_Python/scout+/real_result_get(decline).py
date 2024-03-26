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
        
        for i in range(self.bucket_nums):
            one_bucket = []
            for cell_number in range(self.cell_nums):
                one_cell = [0]*6
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
        for idx in range(self.bucket_nums):
            for cell in range(self.cell_nums):
                if self.scout[idx][cell][0] != 0:
                    
                    if self.scout[idx][cell][1] == 0:   # 当前值太小 已经为0
                        self.scout[idx][cell][0] = 0
                        self.scout[idx][cell][2] = 0
                        self.scout[idx][cell][3] = 0
                        self.scout[idx][cell][4] = 0
                        self.scout[idx][cell][5] = 0
                        continue

                    if self.scout[idx][cell][3] == 0 and self.scout[idx][cell][1] >= 64:   # 第一次出现的点当作下降
                        self.scout[idx][cell][2] = self.scout[idx][cell][1]
                        self.scout[idx][cell][1] = 0    # 每周期对Current_value置零
                        self.scout[idx][cell][3] = 1
                        self.scout[idx][cell][4] = 0
                        self.scout[idx][cell][5] = time_windows
                        continue

                    if self.scout[idx][cell][1] < self.scout[idx][cell][2] * self.P:     # 满足增长率P
                        self.scout[idx][cell][3] += 1
                        self.scout[idx][cell][4] = 0
                        self.scout[idx][cell][2] = self.scout[idx][cell][1]
                        if self.scout[idx][cell][3] == self.K:   # 达到成功阈值
                            # 报告为promising flow
                            global num2
                            num2 += 1
                            global real_array       # 报告写入real_array中
                            real_array.append([self.scout[idx][cell][0],self.scout[idx][cell][5],time_windows,1])
                            # 从当前周期重新判定是否为promising flow
                            self.scout[idx][cell][3] -= 1
                    elif self.scout[idx][cell][1] > self.scout[idx][cell][2] * self.Q :  # 衰减过多

                        if self.scout[idx][cell][1] > 64:
                            self.scout[idx][cell][2] = self.scout[idx][cell][1]
                            self.scout[idx][cell][3] = 1
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = time_windows
                        else:
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][1] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0
                            continue
                    else:
                        self.scout[idx][cell][4] += 1
                        if self.scout[idx][cell][4] == self.T:      # 达到失败阈值 直接踢出
                            self.scout[idx][cell][0] = 0
                            self.scout[idx][cell][2] = 0
                            self.scout[idx][cell][3] = 0
                            self.scout[idx][cell][4] = 0
                            self.scout[idx][cell][5] = 0
                    self.scout[idx][cell][1] = 0    # 每周期对Current_value置零


if __name__=="__main__":

    print("Programme is running!!!")
    Infilename = "E:\\research\\grade1\\D-dataset\\stack_overflow"
    Files = os.listdir(Infilename)

    cell_bits = 32+14+14+4+4+12
    cell_nums = 32

    for T_value in [10]:
        time_windows = 0    # 当前窗口
        real_array = []     # 用于保存结果
        num2 = 0        # 保存出现的promising总和
        real_full = 0       # bucket满了的次数
        P = 0.95
        Q = 1.05
        K = 5
        T = T_value

        scoutsketch_real = detect_real(500,cell_bits,cell_nums,P,Q,K,T)

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

                if values <= 15:     #不满足阈值的只检查有没有已经被保存在bucket中 有则加 无则pass
                    scoutsketch_real.checkinsert(key,values)
                else:         # 将size满足大小的插入无限空间的sketch
                    scoutsketch_real.insert(key,values)

            scoutsketch_real.query()

            print("The {}th time window data has been processed!!!".format(time_windows))
            #print("--------------------------------")

        with open("E:\\research\\grade1\\result\\(decline-stack)True.txt", "w") as f:
            f.write(str(real_array))

        print(num2)
        print(real_full)

        if real_full != 0:
            print("full")
            sys.exit()
        print("run over")