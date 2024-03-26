#include "Cell_new.h"
#include "hash.h"
#include <cstring>
#include <cmath>
#include <numeric>
#include <set>
#include <ctime>
#include "Filter_CM.h"
// #include "Filter_CU.h"
#include "scout.h"
using namespace std;

class our
{

public:
    our(double memory, double ratio, int filter_d,int Filter_counter_bits, int Cell_num, int cell_bits, double P,double Q,int K, int T):
        ratio(ratio),filter_d(filter_d),Filter_counter_bits(Filter_counter_bits),Cell_num(Cell_num),cell_bits(cell_bits),P(P),Q(Q),K(K),T(T){
        Mem = memory;
        filter = new Filter_CM((Mem * ratio), filter_d, Filter_counter_bits);
        //memset(filter,0,sizeof((int)(Mem * ratio)/filter_d/Filter_counter_bits));
        scoutsketch = new scout((Mem*(1-ratio)),Cell_num,cell_bits,P,Q,K,T);
        //memset(scoutsketch,0,sizeof((int)(Mem*(1-ratio)/Cell_num/cell_bits)));

    }
    ~our(){}

    void insert(uint64_t id, int current_window) {

		uint32_t pos = scoutsketch->CheckInsert(id);

		if (pos == -1)
			return;

		bool success = filter->insert(id);

		if (!success) {
			scoutsketch->insert(id, current_window);
		}

	}

    void detect(int current) {

		scoutsketch->query(current);
	}


	void refresh() {
		// filter->refresh();
        filter->refresh();
	}

	// std::vector<scoutsketch<uint64_t>> query() {
	// 	return scoutsketch->Record;
	// }

private:
    double Mem;
    double ratio;
    int filter_d;
    int Filter_counter_bits;
    int Cell_num;
    double P;
    double Q;
    int K;
    int T;
    int cell_bits;
    Filter_CM* filter;
    scout* scoutsketch;

       
};

// #endif


