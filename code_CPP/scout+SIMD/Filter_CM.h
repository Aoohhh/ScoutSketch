#ifndef _FILTER_CM_H_
#define _FILTER_CM_H_

#include <cstring>
#include <cmath>
#include <set>
#include <limits.h>
#include "hash.h"

using namespace std;

class Filter_CM {
public:
	Filter_CM(double Memory, int d, int Counter_bits) : d(d), Counter_bits(Counter_bits)
	{
		// cout<<"Memory: "<<Memory<<endl;
		Mem = Memory * 1024 * 8;
		seeds = new uint32_t[d];
		memset(seeds,0,sizeof(uint32_t)* d);
		int flag = 0;
		while (flag == 0) {
			for (int i = 0; i < d; i++) {
				seeds[i] = rand() % 4294899999 + 67297;
			}
			if (seeds[0] != seeds[1]) {
				flag = 1;
			}
		}
		Counter_num = Mem / Counter_bits;
		overflow_size = pow(2, Counter_bits) - 1;
		CBF = new int[Counter_num];
		memset(CBF,0,sizeof(int) * Counter_num) ;
	}

	~Filter_CM() {}

	bool insert(uint64_t id) {
		int changed = 0;
		uint32_t hash_value = hash1(id, seeds[0]);
		for (int i = 0; i < d; i++) {
			uint32_t pos = (hash_value & ((1 << 16) - 1)) % Counter_num;
			hash_value >>= 16;
			if (CBF[pos] < overflow_size) {
				CBF[pos]++;
				changed = 1;
			}
		}
		if (changed == 0)
			return false;
		else
			return true;
	}

	void refresh() {
		memset(CBF, 0, sizeof(int) * Counter_num);
	}

private:
	double Mem;
	int d;
	uint32_t* seeds;
	int Counter_bits;
	int* CBF;
	int Counter_num;
	int overflow_size;
};

#endif




// class Filter_CM {
// public:
// 	Filter_CM(int Memory, int d, int Counter_bits) : d(d), Counter_bits(Counter_bits)
// 	{
// 		Mem = Memory * 1024 * 8;
// 		seeds = std::vector<uint32_t>(d);
// 		for (int i = 0; i < d; i++) {
// 			seeds[i] = rand() % 4294899999 + 67297;
// 		}
// 		std::set<uint32_t>seed_set = std::set<uint32_t>(seeds.begin(), seeds.end());
// 		while (seed_set.size() < d) {
// 			for (int i = 0; i < d; i++) {
// 				seeds[i] = rand() % 4294899999 + 67297;
// 			}
// 			seed_set = std::set<uint32_t>(seeds.begin(), seeds.end());
// 		}
// 		Counter_num = Mem / Counter_bits;
// 		overflow_size = pow(2, Counter_bits) - 1;
// 		CBF = std::vector<int>(Counter_num);
// 	}

// 	~Filter_CM() {}

// 	bool insert(uint64_t id) {
// 		int changed = 0;
// 		for (int i = 0; i < d; i++) {
// 			uint32_t pos = hash1(id, seeds[i]) % Counter_num;
// 			if (CBF[pos] < overflow_size) {
// 				CBF[pos]++;
// 				changed = 1;
// 			}
// 		}
// 		if (changed == 0)
// 			return false;
// 		else
// 			return true;
// 	}

// 	void refresh() {
// 		CBF = std::vector<int>(Counter_num);
// 	}

// private:
// 	int Mem;
// 	int d;
// 	std::vector<uint32_t> seeds;
// 	int Counter_bits;
// 	std::vector<int> CBF;
// 	int Counter_num;
// 	int overflow_size;
// };

// #endif