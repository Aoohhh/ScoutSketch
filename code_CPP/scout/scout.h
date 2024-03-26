#include <cstring>
#include <cmath>
#include <numeric>
#include <set>
#include <limits.h>
#include <fstream>
#include "Filter_CM.h"
// #include "Filter_CU.h"
#include "Cell_new.h"
#include "hash.h"
#include <cfloat>
#include <random>
#include "ctime"
#define N 999

using namespace std;
ofstream out;
const string filename = "result.txt";

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
    std::vector<std::vector<Cell_new>> DS;


public:
    scout(int mem,int cell_num,int scout_cell_bits,double P,double Q,int K,int T):
        cell_num(cell_num),scout_cell_bits(scout_cell_bits),P(P),Q(Q),K(K),T(T)
    {
        out.open(filename);
        memory = mem *1024*8;
        scout_cell_bits = 32+14+14+3+4+12+1+12;
        bucket_num = memory / cell_num / scout_cell_bits;
        seed = rand() % 4294899999 + 67297;
        DS = std::vector<std::vector<Cell_new>>(bucket_num);
        for (int i = 0 ; i < bucket_num; i++){
            for (int j = 0; j < cell_num; j++){
                DS[i].push_back(Cell_new());
            }
        }
    }

    ~scout(){
        out.close();
    }


    uint32_t CheckInsert(uint64_t flowid)
    {
        uint32_t pos = hash1(flowid, seed) % bucket_num;
        for (int i = 0; i < cell_num; i++)
        {
            if( DS[pos][i].id == flowid)
            {
                DS[pos][i].structure[0] += 1;
                return -1;
            }
        }
        return 1;
    }



    void insert(uint64_t flowid,int timewindows)        // protect***************************
    {
        // bool flag = false;
        uint32_t pos = hash1(flowid, seed) % bucket_num;
        double mindelta = -1;
        int kick_cell = -1;
        for (int i = 0; i < cell_num; i++)
        {
            if (DS[pos][i].id == 0){
                DS[pos][i].id = flowid;
                DS[pos][i].structure[0] += pow(2,4);//////////////////////////////
                DS[pos][i].start_time = timewindows;
                return;
            }
            else
            {
                if (DS[pos][i].structure[2] != 0){
                    int interval = timewindows - DS[pos][i].start_time;
                    int delta = interval / DS[pos][i].structure[2];
                    if (interval > 5 && delta > mindelta)
                    {
                        kick_cell = i;
                        mindelta = delta;
                    }
                }
            }
        }
        if (kick_cell!= -1 && mindelta > 3){           // 7 为filter阈值
            DS[pos][kick_cell].id = flowid;
            DS[pos][kick_cell].structure[0] = pow(2,4);/////////////////////////////
            DS[pos][kick_cell].structure[1] = 0;
            DS[pos][kick_cell].structure[2] = 1;
            DS[pos][kick_cell].structure[3] = 0;
            DS[pos][kick_cell].start_time = timewindows;
        }
        
    }


//     void insert(uint64_t flowid,int timewindows)        // Space Saving************************
//     {
//         int temp_cell = -1;
//         double temp_min = DBL_MAX;
//         uint32_t pos = hash1(flowid, seed) % bucket_num;
//         for(int i = 0 ; i < cell_num;i++)
//         {
//             if(DS[pos][i].id==flowid)
//             {
//                 DS[pos][i].structure[0]+=1;
//                 return;
//             }
//         }
//         for(int i = 0; i <cell_num;i++){
//             if(DS[pos][i].id == 0){
//                 DS[pos][i].id = flowid;
//                 DS[pos][i].structure[0] += pow(2,4);  // filter的阈值 后续可能需要调整的参数****
//                 DS[pos][i].start_time = timewindows;
//                 return;
//             }
//             else{
//                 if(DS[pos][i].structure[0]<temp_min){
//                     temp_min = DS[pos][i].structure[0];
//                     temp_cell = i;
//                 }
//             }
//         }
//         DS[pos][temp_cell].id = flowid;
//         DS[pos][temp_cell].structure[0] = timewindows;
//     }


//     void insert(uint64_t flowid,int timewindows)        // RA policy************************
//     {
//         int temp_cell = -1;
//         double temp_min = DBL_MAX;
//         uint32_t pos = hash1(flowid, seed) % bucket_num;
//         for(int i = 0 ; i < cell_num;i++)
//         {
//             if(DS[pos][i].id==flowid)
//             {
//                 DS[pos][i].structure[0]+=1;
//                 return;
//             }
//         }
//         for(int i = 0; i <cell_num;i++){
//             if(DS[pos][i].id == 0){
//                 DS[pos][i].id = flowid;
//                 DS[pos][i].structure[0] += pow(2,4);  // filter的阈值 后续可能需要调整的参数****
//                 DS[pos][i].start_time = timewindows;
//                 return;
//             }
//             else{
//                 if(DS[pos][i].structure[0]<temp_min){
//                     temp_min = DS[pos][i].structure[0];
//                     temp_cell = i;
//                 }
//             }
//         }
        
//         float random = 0;
//         srand(time(NULL));
//         random = rand()%(N+1) / (float)(N+1);
//         // std::mt19937 rng(std::random_device{}());
//         // // 创建一个均匀分布，指定范围为[0, 1)
//         // std::uniform_real_distribution<double> dist(0.0, 1.0);
//         // 生成随机浮点数
//         // double randomNum = dist(rng);
//         if(random < 1/(1+temp_min)){
//             DS[pos][temp_cell].id = flowid;
//             DS[pos][temp_cell].structure[0] = timewindows;
//         }
//     }


//     void insert(uint64_t flowid,int timewindows)        // Frequent************************
//         {
//             int temp_cell = -1;
//             double temp_min = DBL_MAX;
//             uint32_t pos = hash1(flowid, seed) % bucket_num;
//             for(int i = 0 ; i < cell_num;i++)
//             {
//                 if(DS[pos][i].id==flowid)
//                 {
//                     DS[pos][i].structure[0]+=1;
//                     return;
//                 }
//             }
//             for(int i = 0; i <cell_num;i++){
//                 if(DS[pos][i].id == 0){
//                     DS[pos][i].id = flowid;
//                     DS[pos][i].structure[0] += pow(2,4);  // filter的阈值 
//                     DS[pos][i].start_time = timewindows;
//                     return;
//                 }
//                 else{
//                     if(DS[pos][i].structure[0]<temp_min){
//                         temp_min = DS[pos][i].structure[0];
//                         temp_cell = i;
//                     }
//                 }
//             }
//             DS[pos][temp_cell].structure[0]-=1;
//             if(DS[pos][temp_cell].structure[0]==0){
//                 DS[pos][temp_cell].id = flowid;
//                 DS[pos][temp_cell].structure[0] = 1;
//                 DS[pos][temp_cell].start_time = timewindows;
//             }
//         }


//     void insert(uint64_t flowid,int timewindows)        // HeavyGuardian************************
//     {
//         int temp_cell = -1;
//         double temp_min = DBL_MAX;
//         uint32_t pos = hash1(flowid, seed) % bucket_num;
//         for(int i = 0 ; i < cell_num;i++)
//         {
//             if(DS[pos][i].id==flowid)
//             {
//                 DS[pos][i].structure[0]+=1;
//                 return;
//             }
//         }
//         for(int i = 0; i <cell_num;i++){
//             if(DS[pos][i].id == 0){
//                 DS[pos][i].id = flowid;
//                 DS[pos][i].structure[0] += pow(2,4);  // filter的阈值 
//                 DS[pos][i].start_time = timewindows;
//                 return;
//             }
//             else{
//                 if(DS[pos][i].structure[0]<temp_min){
//                     temp_min = DS[pos][i].structure[0];
//                     temp_cell = i;
//                 }
//             }
//         }
        
//         float random = 0;
//         srand(time(NULL));
//         random = rand()%(N+1) / (float)(N+1);
//         // std::mt19937 rng(std::random_device{}());
//         // // 创建一个均匀分布，指定范围为[0, 1)
//         // std::uniform_real_distribution<double> dist(0.0, 1.0);
//         // double randomNum = dist(rng);
//         if(random < pow(1.08,(-temp_min))){
//             DS[pos][temp_cell].structure[1] -= 1;
//             if(DS[pos][temp_cell].structure[1] == 0){
//                 DS[pos][temp_cell].id = flowid;
//                 DS[pos][temp_cell].structure[1] = 1;
//                 DS[pos][temp_cell].structure[0] = timewindows;
//             }
//         }
//     }



//     void query(int timewindows){    // ScoutSketch query - decline
//         for (int i = 0; i < bucket_num; i++)
//         {
//             for (int j = 0; j < cell_num; j++)
//             {
//                 if (DS[i][j].id != 0)
//                 {
//                     if (DS[i][j].structure[0] == 0)
//                     {   //当前值过小 已经为0
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].start_time = 0;
//                             continue;
//                     }

//                     if(DS[i][j].structure[2]==0 && DS[i][j].structure[0]>=64)
//                     {
//                         DS[i][j].structure[1] =DS[i][j].structure[0];
//                         DS[i][j].structure[0] = 0;
//                         DS[i][j].structure[2] = 1;
//                         DS[i][j].structure[3] = 0;
//                         DS[i][j].start_time = timewindows;
//                         continue;
//                     }

//                     if(DS[i][j].structure[0] < DS[i][j].structure[1] * P)
//                     {
//                         DS[i][j].structure[2] += 1;
//                         DS[i][j].structure[3] = 0;
//                         DS[i][j].structure[1] = DS[i][j].structure[0];
//                         if(DS[i][j].structure[2] == K)
//                         {
//                             out << DS[i][j].id << " " << DS[i][j].start_time << " " << timewindows << '\n';
//                             DS[i][j].structure[2] -= 1;
//                         }
//                     }
//                     else if (DS[i][j].structure[0] > DS[i][j].structure[1] * Q)
//                     {
//                         if(DS[i][j].structure[0] > 64)
//                         {
//                             DS[i][j].structure[1] = DS[i][j].structure[0];
//                             DS[i][j].structure[2] = 1;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].start_time = timewindows;
//                         }
//                         else
//                         {
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[0] = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].start_time = 0;
//                             continue;
//                         }
//                     }
//                     else
//                     {
//                         DS[i][j].structure[3] += 1;
//                         if (DS[i][j].structure[3] == T)
//                         {
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].start_time = 0;
//                         }
//                     }
//                     DS[i][j].structure[0] = 0;
//                 }
//             }           
//         }   
//     }

//      void query(int timewindows){    // ScoutSketch query - increase
//         for (int i = 0; i < bucket_num; i++)
//         {
//             for (int j = 0; j < cell_num; j++)
//             {
//                 if (DS[i][j].id != 0)
//                 {
//                     if(DS[i][j].structure[0] > DS[i][j].structure[1] * P)
//                     {
//                         DS[i][j].structure[2] += 1;
//                         DS[i][j].structure[3] = 0;
//                         DS[i][j].structure[1] = DS[i][j].structure[0];
//                         if(DS[i][j].structure[2] == K)
//                         {
//                             out << DS[i][j].id << " " << DS[i][j].start_time << " " << timewindows << '\n';
//                             DS[i][j].structure[2] -= 1;
//                         }
//                     }
//                     else if(DS[i][j].structure[0] < DS[i][j].structure[1] * Q)
//                     {   
//                         if(DS[i][j].structure[0]<16)
//                         {
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].start_time = 0;
//                         }
//                         else
//                         {
//                             DS[i][j].structure[1] = DS[i][j].structure[0];
//                             DS[i][j].structure[2] = 1;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].start_time = timewindows;
//                         }
//                     }
//                     else
//                     {
//                         DS[i][j].structure[3] += 1;
//                         if (DS[i][j].structure[3] == T){
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].start_time = 0;
//                         }
//                     }
//                     DS[i][j].structure[0] = 0;
//                 }
//             }
//         }
//     }


//     void query(int timewindows){    // ScoutSketch+ query
//         for (int i = 0; i < bucket_num; i++)
//         {
//             for (int j = 0; j < cell_num; j++)
//             {
//                 if (DS[i][j].id != 0)
//                 {
//                     // if(DS[i][j].id == 3573875943){
//                     //     if(timewindows <= 9){
//                     //     cout<<DS[i][j].structure[0]<<" ";
//                     //     cout<<DS[i][j].structure[1]<<" ";
//                     //     cout<<DS[i][j].structure[2]<<" ";
//                     //     cout<<DS[i][j].structure[3]<<" ";
//                     //     cout<<DS[i][j].structure[4]<<" ";
//                     //     cout<<DS[i][j].structure[5]<<" ";
//                     //     cout<<DS[i][j].start_time<<endl;
//                     //     }
//                     //     else{
//                     //         std::exit(0);
//                     //     }
//                     // }
//                     if(DS[i][j].structure[0] > DS[i][j].structure[1] * P)
//                     {
//                         if(DS[i][j].structure[0] < pow(2,4))  ////////////////////////////////////////////
//                         {
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[0] = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].structure[4] = 0;  //temp time
//                             DS[i][j].structure[5] = 0;  //flag bit
//                             DS[i][j].start_time = 0;
//                             continue;
//                         }
//                         if(DS[i][j].structure[5] == 0)
//                         {
//                             DS[i][j].structure[2] += 1;
//                             if(DS[i][j].structure[2] == K)
//                             {
//                                 //out << DS[i][j].id << " " << DS[i][j].start_time << " " << timewindows << '\n';
//                                 DS[i][j].structure[2] -= 1;
//                             }
//                         }
//                         else
//                         {
//                             if(DS[i][j].structure[1] < pow(2,4))////////////////////
//                             {
//                                 DS[i][j].structure[2] = 1;
//                                 DS[i][j].start_time = timewindows;
//                             }
//                             else
//                             {
//                                 DS[i][j].structure[2] = 2;
//                                 DS[i][j].start_time = DS[i][j].structure[4];
//                             }
//                             DS[i][j].structure[5] = 0;
//                         }
//                         DS[i][j].structure[1] = DS[i][j].structure[0];
//                         DS[i][j].structure[3] = 0;       
//                         DS[i][j].structure[4] = timewindows;
//                     }
//                     else if( DS[i][j].structure[0] < DS[i][j].structure[1] * Q)
//                     {
//                         if( DS[i][j].structure[0]==0){
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[0] = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].structure[4] = 0;
//                             DS[i][j].structure[5] = 0;
//                             DS[i][j].start_time = 0;
//                             continue;
//                         }
                       
//                         if(DS[i][j].structure[5] == 0)
//                         {
//                             if(DS[i][j].structure[1] < pow(2,6))      ////***************下降阈值64 为可变参数
//                             {
//                                 if(DS[i][j].structure[0]>=pow(2,4))///////////////////////
//                                 {
//                                     DS[i][j].structure[1] = DS[i][j].structure[0];
//                                     DS[i][j].structure[0] = 0;
//                                     DS[i][j].structure[2] = 1;
//                                     DS[i][j].structure[3] = 0;
//                                     DS[i][j].structure[4] = timewindows;
//                                     DS[i][j].start_time = timewindows;
//                                     continue;
//                                 }
//                                 else
//                                 {
//                                     DS[i][j].id = 0;
//                                     DS[i][j].structure[0] = 0;
//                                     DS[i][j].structure[1] = 0;
//                                     DS[i][j].structure[2] = 0;
//                                     DS[i][j].structure[3] = 0;
//                                     DS[i][j].structure[4] = 0;
//                                     DS[i][j].structure[5] = 0;
//                                     DS[i][j].start_time = 0;
//                                     continue;
//                                 }
//                             }
//                             if(DS[i][j].structure[2]!=1)
//                             {
//                                 DS[i][j].start_time = DS[i][j].structure[4];
//                             }
//                             //DS[i][j].structure[1] = DS[i][j].structure[0];
//                             DS[i][j].structure[2] = 2;
//                             DS[i][j].structure[5] = 1;
//                         }
//                         else
//                         {
//                             DS[i][j].structure[2] += 1;
                            
//                             if(DS[i][j].structure[2] == K)
//                             {
//                                 //out << DS[i][j].id << " " << DS[i][j].start_time << " " << timewindows << '\n';
//                                 DS[i][j].structure[2] -= 1;
//                             }
//                         }
//                         DS[i][j].structure[1] = DS[i][j].structure[0];
//                         DS[i][j].structure[3] = 0;
//                         DS[i][j].structure[4] = timewindows;
//                     }
//                     else
//                     {
//                         DS[i][j].structure[3] += 1;
//                         if( DS[i][j].structure[3] == T)
//                         {
//                             DS[i][j].id = 0;
//                             DS[i][j].structure[0] = 0;
//                             DS[i][j].structure[1] = 0;
//                             DS[i][j].structure[2] = 0;
//                             DS[i][j].structure[3] = 0;
//                             DS[i][j].structure[4] = 0;
//                             DS[i][j].structure[5] = 0;
//                             DS[i][j].start_time = 0;
//                             continue;
//                         }
//                     }
//                     DS[i][j].structure[0] = 0;
//                 }
//             }
//         }
//     }

void query(int timewindows){    // ScoutSketch query
        for (int i = 0; i < bucket_num; i++)
        {
            for (int j = 0; j < cell_num; j++)
            {
                if (DS[i][j].id != 0)
                {
                    if(DS[i][j].structure[0] > DS[i][j].structure[1] * P)
                    {
                        DS[i][j].structure[2] += 1;
                        DS[i][j].structure[3] = 0;
                        DS[i][j].structure[1] = DS[i][j].structure[0];
                        if(DS[i][j].structure[2] == K)
                        {
                            out << DS[i][j].id << " " << DS[i][j].start_time << " " << timewindows << '\n';
                            DS[i][j].structure[2] -= 1;
                        }
                    }
                    else if(DS[i][j].structure[0] < DS[i][j].structure[1] * Q)
                    {   
                            DS[i][j].id = 0;
                            DS[i][j].structure[1] = 0;
                            DS[i][j].structure[2] = 0;
                            DS[i][j].structure[3] = 0;
                            DS[i][j].start_time = 0;
               
                    }
                    else
                    {
                        DS[i][j].structure[3] += 1;
                        if (DS[i][j].structure[3] == T){
                            DS[i][j].id = 0;
                            DS[i][j].structure[1] = 0;
                            DS[i][j].structure[2] = 0;
                            DS[i][j].structure[3] = 0;
                            DS[i][j].start_time = 0;
                        }
                    }
                    DS[i][j].structure[0] = 0;
                }
            }
        }
    }
};
