#ifndef _CELL_NEW_H_
#define _CELL_NEW_H_

#include <cstring>
#include "hash.h"

using namespace std;


class Cell_new {

public:
	// uint64_t id;
	int Counter_bits;
	int h;
	int* structure;
	int start_time;

	Cell_new()
	{
		// id = 0;
		Counter_bits = 14;
		h = 3;
		structure = new int[2 * h];
		memset(structure, 0, sizeof(int) * 2 * h);
		start_time = 0;
	}

	Cell_new(int Counter_bits, int h, int start_time) : Counter_bits(Counter_bits), h(h), start_time(start_time)
	{
		structure = new int[2*h];
		memset(structure, 0, sizeof(int) * 2 * h);
	}
	~Cell_new() {}
};


#endif