#ifndef _FILTER_CU_H_
#define _FILTER_CU_H_

#include <cstring>
#include <cmath>
#include <set>
#include <limits.h>
#include "hash.h"
using namespace std;

class Filter_CU {
public:
	Filter_CU(double Memory, int d, int Counter_bits) : d(d), Counter_bits(Counter_bits)
	{
		Mem = Memory * 1024 * 8;
		seeds = new uint32_t[d];
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
		memset(CBF, 0, sizeof(int) * Counter_num);
	}

	~Filter_CU() {}

	bool insert(uint64_t id) {
		int min = INT_MAX;
		uint32_t hash_value = hash1(id, seeds[0]);
		for (int i = 0; i < d; i++) {
			uint32_t pos = (hash_value & ((1 << 16) - 1)) % Counter_num;
			hash_value >>= 16;
			if (CBF[pos] < min)
				min = CBF[pos];
		}
		if (min == overflow_size)
			return false;
		hash_value = hash1(id, seeds[0]);
		for (int j = 0; j < d; j++) {
			uint32_t pos = (hash_value & ((1 << 16) - 1)) % Counter_num;
			hash_value >>= 16;
			if (CBF[pos] == min)
				CBF[pos]++;
		}
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