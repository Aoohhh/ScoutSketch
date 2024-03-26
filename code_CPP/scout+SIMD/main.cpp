#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <fstream>
#include <time.h>
#include <map>
#include <cmath>
#include <vector>
#include <unordered_map>
#include <map>
#include <unordered_set>
#include <chrono>
#include <regex>
#include <cstring>
// #include "sscanf"
#include "our.h"

using namespace std;

uint32_t parseIPV4string(char const * ipAddress)
{
    unsigned int ipbytes[4];

    if ( 4 != sscanf(ipAddress, "%u.%u.%u.%u", &ipbytes[0], &ipbytes[1], &ipbytes[2], &ipbytes[3]) )
         return 0;   // or some other indicator or error

    return ipbytes[3] + ipbytes[2] * 0x100 + ipbytes[1] * 0x10000ul + ipbytes[0] * 0x1000000ul;
}

int main() {
    // std::ios::sync_with_stdio(false);
    const char* file = "../../CAIDA19.txt";
    uint64_t* insert = (uint64_t*)malloc(30000000 * sizeof(uint64_t));
    unordered_map<uint64_t, int> unmp;
    unordered_set<uint32_t> myset;

	srand((unsigned)time(NULL));
	uint32_t flow_num = 30000000;
    unmp.clear();

    int package_num = 0;
    char data[100];
    const char* d = " ";
    ifstream fin(file);
    while (fin.getline(data, 100) && package_num < 30000000) {

        char* p = strtok(data, d);
		//uint32_t ip = atoi(p);
        uint32_t ip = parseIPV4string(p);
		insert[package_num] = ip;
        myset.insert(ip);
        //unmp[ip]++;
        package_num++;
    }
    //printf("dataset name: %s\n", file);
    //printf("total packet size = %d\n", package_num);
    //printf("distinct item number = %d\n",myset.size());

    cout << "dataset name : " << file << endl;
    cout << "total packet size : " << package_num << endl;
    cout << "distinct item number : " << myset.size() << endl;


	int count = 0;   //  T = 3000
	uint64_t** Flow_list = new uint64_t*[3000];
	for (int i = 0; i < 3000; i++) {
		Flow_list[i] = new uint64_t[10000];
		for (int j = 0; j < 10000; j++) {
			uint64_t id = insert[count];
			Flow_list[i][j] = id;
			count++;
		}
    }

    // 创建一个包含5个元素的数组
    double arr1[5]={2,4,6,8,10};
    // 打印数组

    for (unsigned int i = 0; i < 5; i++)
    {
        double mem = double(arr1[i]);

        int Filter_d = 2;
        int Filter_counter_bits = 4;
        int Cell_num = 4;
        int Cell_bits = 32+14+14+3+4+12+1+12;
        double P = 1.05;
        double Q = 0.95;
        int K = 5;
        int T = 10;
        double Memory_ratio = 0.3;

        our* ourscout = new our(mem,Memory_ratio,Filter_d,Filter_counter_bits,Cell_num,Cell_bits,P,Q,K,T);

        auto scout_start = std::chrono::steady_clock::now();

        for (int i = 0; i < 3000; i++) {
            for (int j = 0; j < 10000; j++) {
                ourscout->insert(Flow_list[i][j], i+1);
            }

            ourscout->detect(i + 1);
            ourscout->refresh();
        }


        auto scout_end = std::chrono::steady_clock::now();
        std::chrono::duration<double> scout_span = std::chrono::duration_cast<std::chrono::duration<double>>(scout_end - scout_start);
        std::cout << "Our Sketch:" << std::endl;
        std::cout << "Throughput(Mips):     " << flow_num / (1000 * 1000 * scout_span.count()) << "\n\n";
        //return 0;
    }
}