#ifndef _SCOUT_H_
#define _SCOUT_H_

#include <cstring>
#include <cmath>
#include <numeric>
#include <set>
#include <limits.h>

#include <immintrin.h>
#include <emmintrin.h>
#include <smmintrin.h>
#include <fstream>
#include "Filter_CM.h"
// #include "Filter_CU.h"
#include "Cell_new.h"
#include "hash.h"
#include <cfloat>
#include <random>
#include "ctime"

using namespace std;
ofstream out;
const string filename = "result.txt";

inline int SIMD_Match_4(uint64_t* ID, uint64_t key) {

    const __m256i item = _mm256_set1_epi64x(key);
    int matched;
    __m256i* keys_p = (__m256i*) ID; 
    //_mm256_setr_epi64x(reinterpret_cast<long long int>(ID), reinterpret_cast<long long int>(ID), reinterpret_cast<long long int>(ID), reinterpret_cast<long long int>(ID));
    // 修改后的代码
    __m256i temp = _mm256_loadu_si256(keys_p); // 加载非对齐的数据
    __m256i a_comp = _mm256_cmpeq_epi64(item, temp); // 进行比较
    // __m256i a_comp = _mm256_cmpeq_epi64(item, keys_p[0]);
    matched = _mm256_movemask_epi8(a_comp);
    if (matched != 0) {
        int matched_index = _tzcnt_u32((uint32_t)matched) >> 3;
        return matched_index;
    }
    else return -1;
}



class scout
{
private:
    double memory;
    uint32_t seed;
    int bucket_num;
    int cell_num;
    int scout_cell_bits;
    double P;
    double Q;
    int K;
    int T;
    uint64_t** Id;
    Cell_new** DS;

public:
    scout(int mem, int cell_num, int scout_cell_bits, double P, double Q, int K, int T) :
        cell_num(cell_num), scout_cell_bits(scout_cell_bits), P(P), Q(Q), K(K), T(T)
    {
        out.open(filename, ios::ate);
        memory = mem * 1024 * 8;
        bucket_num = memory / cell_num / scout_cell_bits;
        seed = rand() % 4294899999 + 67297;
        DS = new Cell_new * [bucket_num];
        for (int i = 0; i < bucket_num; i++) {
            DS[i] = new Cell_new[cell_num];
            for (int j = 0; j < cell_num; j++) {
                DS[i][j] = Cell_new();
            }
        }
        Id = new uint64_t * [bucket_num];
        for (int i = 0; i < bucket_num; ++i) {
            Id[i] = new uint64_t[cell_num];
            memset(Id[i], 0, sizeof(uint64_t) * cell_num);
        }
    }

    ~scout() {
        // out.close();

        // 释放 DS 的内存
        for (int i = 0; i < bucket_num; i++) {
            delete[] DS[i];
        }
        delete[] DS;

        // 释放 Id 的内存
        for (int i = 0; i < bucket_num; i++) {
            delete[] Id[i];
        }
        delete[] Id;

        out.close();
    }


    uint32_t CheckInsert(uint64_t flowid)
    {
        uint32_t pos = hash1(flowid, seed) % bucket_num;
        int j;
        j = SIMD_Match_4(Id[pos], flowid);
        if (j >= 0) {
            DS[pos][j].structure[0] += 1;
            return -1;
        }
        return 1;
    }



    void insert(uint64_t flowid, int timewindows)        // protect***************************
    {
        uint32_t pos = hash1(flowid, seed) % bucket_num;
        double mindelta = -1;
        int kick_cell = -1;

        // SIMD
        int j;
        j = SIMD_Match_4(Id[pos], 0);
        if (j >= 0) {       // PASS
            Id[pos][j] = flowid;
            DS[pos][j].structure[0] += 16;//////////////////////////////
            DS[pos][j].start_time = timewindows;
            return;
        }

         for (int i = 0; i < cell_num; i++)
         {
             if (DS[pos][i].structure[2] != 0) {
                 int interval = timewindows - DS[pos][i].start_time;
                 int delta = interval / DS[pos][i].structure[2];
                 if (interval > 5 && delta > mindelta)
                 {
                     kick_cell = i;
                     mindelta = delta;
                 }
             }
         }
         if (kick_cell != -1 && mindelta > 3) {           // 7 为filter阈值
             Id[pos][kick_cell] = flowid;
             DS[pos][kick_cell].structure[0] = pow(2, 4);/////////////////////////////
             DS[pos][kick_cell].structure[1] = 0;
             DS[pos][kick_cell].structure[2] = 1;
             DS[pos][kick_cell].structure[3] = 0;
             DS[pos][kick_cell].start_time = timewindows;
         }
    }


    void query(int timewindows) {    // both
        for (int i = 0; i < bucket_num; i++)
        {
            for (int j = 0; j < cell_num; j++)
            {
                if (Id[i][j] != 0)
                {
                    if (DS[i][j].structure[0] > DS[i][j].structure[1] * P)
                    {
                        if (DS[i][j].structure[0] < 16)  ////////////////////////////////////////////
                        {
                            Id[i][j] = 0;
                            DS[i][j].structure[0] = 0;
                            DS[i][j].structure[1] = 0;
                            DS[i][j].structure[2] = 0;
                            DS[i][j].structure[3] = 0;
                            DS[i][j].structure[4] = 0;  //temp time
                            DS[i][j].structure[5] = 0;  //flag bit
                            DS[i][j].start_time = 0;
                            continue;
                        }
                        if (DS[i][j].structure[5] == 0)
                        {
                            DS[i][j].structure[2] += 1;
                            if (DS[i][j].structure[2] == K)
                            {
                                DS[i][j].structure[2] -= 1;
                            }
                        }
                        else
                        {
                            if (DS[i][j].structure[1] <16)////////////////////
                            {
                                DS[i][j].structure[2] = 1;
                                DS[i][j].start_time = timewindows;
                            }
                            else
                            {
                                DS[i][j].structure[2] = 2;
                                DS[i][j].start_time = DS[i][j].structure[4];
                            }
                            DS[i][j].structure[5] = 0;
                        }
                        DS[i][j].structure[1] = DS[i][j].structure[0];
                        DS[i][j].structure[3] = 0;
                        DS[i][j].structure[4] = timewindows;
                    }
                    else if (DS[i][j].structure[0] < DS[i][j].structure[1] * Q)
                    {
                        if (DS[i][j].structure[0] == 0) {
                            Id[i][j] = 0;
                            DS[i][j].structure[0] = 0;
                            DS[i][j].structure[1] = 0;
                            DS[i][j].structure[2] = 0;
                            DS[i][j].structure[3] = 0;
                            DS[i][j].structure[4] = 0;
                            DS[i][j].structure[5] = 0;
                            DS[i][j].start_time = 0;
                            continue;
                        }
                        // 
                        if (DS[i][j].structure[5] == 0)
                        {
                            if (DS[i][j].structure[1] < 64)      ////***************下降阈值64 为可变参数
                            {
                                if (DS[i][j].structure[0] >= 16)///////////////////////
                                {
                                    DS[i][j].structure[1] = DS[i][j].structure[0];
                                    DS[i][j].structure[0] = 0;
                                    DS[i][j].structure[2] = 1;
                                    DS[i][j].structure[3] = 0;
                                    DS[i][j].structure[4] = timewindows;
                                    DS[i][j].start_time = timewindows;
                                    continue;
                                }
                                else
                                {
                                    Id[i][j] = 0;
                                    DS[i][j].structure[0] = 0;
                                    DS[i][j].structure[1] = 0;
                                    DS[i][j].structure[2] = 0;
                                    DS[i][j].structure[3] = 0;
                                    DS[i][j].structure[4] = 0;
                                    DS[i][j].structure[5] = 0;
                                    DS[i][j].start_time = 0;
                                    continue;
                                }
                            }
                            if (DS[i][j].structure[2] != 1)
                            {
                                DS[i][j].start_time = DS[i][j].structure[4];
                            }
                            DS[i][j].structure[1] = DS[i][j].structure[0];
                            DS[i][j].structure[2] = 2;
                            DS[i][j].structure[5] = 1;
                        }
                        else
                        {
                            DS[i][j].structure[2] += 1;

                            if (DS[i][j].structure[2] == K)
                            {
                                out << Id[i][j] << " " << DS[i][j].start_time << " " << timewindows << '\n';
                                DS[i][j].structure[2] -= 1;
                            }
                        }
                        DS[i][j].structure[1] = DS[i][j].structure[0];
                        DS[i][j].structure[3] = 0;
                        DS[i][j].structure[4] = timewindows;
                    }
                    else
                    {
                        DS[i][j].structure[3] += 1;
                        if (DS[i][j].structure[3] == T)
                        {
                            Id[i][j] = 0;
                            DS[i][j].structure[0] = 0;
                            DS[i][j].structure[1] = 0;
                            DS[i][j].structure[2] = 0;
                            DS[i][j].structure[3] = 0;
                            DS[i][j].structure[4] = 0;
                            DS[i][j].structure[5] = 0;
                            DS[i][j].start_time = 0;
                            continue;
                        }
                    }
                    DS[i][j].structure[0] = 0;
                }
            }
        }
    }
 
    // void query(int timewindows){    // decline
    //     for (int i = 0; i < bucket_num; i++)
    //     {
    //         for (int j = 0; j < cell_num; j++)
    //         {
    //             if (Id[i][j] != 0)
    //             {
    //                 if (DS[i][j].structure[0] == 0)
    //                 {   //当前值过小 已经为0
    //                         Id[i][j] = 0;
    //                         DS[i][j].structure[1] = 0;
    //                         DS[i][j].structure[2] = 0;
    //                         DS[i][j].structure[3] = 0;
    //                         DS[i][j].start_time = 0;
    //                         continue;
    //                 }

    //                 if(DS[i][j].structure[2]==0 && DS[i][j].structure[0]>=64)
    //                 {
    //                     DS[i][j].structure[1] =DS[i][j].structure[0];
    //                     DS[i][j].structure[0] = 0;
    //                     DS[i][j].structure[2] = 1;
    //                     DS[i][j].structure[3] = 0;
    //                     DS[i][j].start_time = timewindows;
    //                     continue;
    //                 }

    //                 if(DS[i][j].structure[0] < DS[i][j].structure[1] * P)
    //                 {
    //                     DS[i][j].structure[2] += 1;
    //                     DS[i][j].structure[3] = 0;
    //                     DS[i][j].structure[1] = DS[i][j].structure[0];
    //                     if(DS[i][j].structure[2] == K)
    //                     {
    //                         out << Id[i][j] << " " << DS[i][j].start_time << " " << timewindows << '\n';
    //                         DS[i][j].structure[2] -= 1;
    //                     }
    //                 }
    //                 else if (DS[i][j].structure[0] > DS[i][j].structure[1] * Q)
    //                 {
    //                     if(DS[i][j].structure[0] > 64)
    //                     {
    //                         DS[i][j].structure[1] = DS[i][j].structure[0];
    //                         DS[i][j].structure[2] = 1;
    //                         DS[i][j].structure[3] = 0;
    //                         DS[i][j].start_time = timewindows;
    //                     }
    //                     else
    //                     {
    //                         Id[i][j] = 0;
    //                         DS[i][j].structure[0] = 0;
    //                         DS[i][j].structure[1] = 0;
    //                         DS[i][j].structure[2] = 0;
    //                         DS[i][j].structure[3] = 0;
    //                         DS[i][j].start_time = 0;
    //                         continue;
    //                     }
    //                 }
    //                 else
    //                 {
    //                     DS[i][j].structure[3] += 1;
    //                     if (DS[i][j].structure[3] == T)
    //                     {
    //                         Id[i][j] = 0;
    //                         DS[i][j].structure[1] = 0;
    //                         DS[i][j].structure[2] = 0;
    //                         DS[i][j].structure[3] = 0;
    //                         DS[i][j].start_time = 0;
    //                     }
    //                 }
    //                 DS[i][j].structure[0] = 0;
    //             }
    //         }           
    //     }   
    // }

    //  void query(int timewindows){    // increase
    //     for (int i = 0; i < bucket_num; i++)
    //     {
    //         for (int j = 0; j < cell_num; j++)
    //         {
    //             if (Id[i][j] != 0)
    //             {
    //                 if(DS[i][j].structure[0] > DS[i][j].structure[1] * P)
    //                 {
    //                     DS[i][j].structure[2] += 1;
    //                     DS[i][j].structure[3] = 0;
    //                     DS[i][j].structure[1] = DS[i][j].structure[0];
    //                     if(DS[i][j].structure[2] == K)
    //                     {
    //                         out << Id[i][j] << " " << DS[i][j].start_time << " " << timewindows << '\n';
    //                         DS[i][j].structure[2] -= 1;
    //                     }
    //                 }
    //                 else if(DS[i][j].structure[0] < DS[i][j].structure[1] * Q)
    //                 {   // 检测是否可以当作新的增长起点
    //                     if(DS[i][j].structure[0]<16)
    //                     {
    //                         Id[i][j] = 0;
    //                         DS[i][j].structure[1] = 0;
    //                         DS[i][j].structure[2] = 0;
    //                         DS[i][j].structure[3] = 0;
    //                         DS[i][j].start_time = 0;
    //                     }
    //                     else
    //                     {
    //                         DS[i][j].structure[1] = DS[i][j].structure[0];
    //                         DS[i][j].structure[2] = 1;
    //                         DS[i][j].structure[3] = 0;
    //                         DS[i][j].start_time = timewindows;
    //                     }
    //                 }
    //                 else
    //                 {
    //                     DS[i][j].structure[3] += 1;
    //                     if (DS[i][j].structure[3] == T){
    //                         Id[i][j] = 0;
    //                         DS[i][j].structure[1] = 0;
    //                         DS[i][j].structure[2] = 0;
    //                         DS[i][j].structure[3] = 0;
    //                         DS[i][j].start_time = 0;
    //                     }
    //                 }
    //                 DS[i][j].structure[0] = 0;
    //             }
    //         }
    //     }
    // }
};
#endif
